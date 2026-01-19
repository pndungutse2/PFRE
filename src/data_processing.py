import re
from pathlib import Path
import pdfplumber
import pandas as pd

# Regex patterns
DATE_RE = re.compile(r'^\d{2}/\d{2}\s')  # Matches "MM/DD " at start of line
AMOUNT_RE = re.compile(r'-?\d{1,3}(?:,\d{3})*\.\d{2}')  # Matches currency amounts

def parse_chase_statement(pdf_path: Path) -> pd.DataFrame:
    """
    Parse Chase bank statement PDF and extract transaction details.
    
    Args:
        pdf_path: Path to the Chase statement PDF file
        
    Returns:
        DataFrame with columns: date, description, amount, balance, source_file
    """
    # Extract year from filename (first 4 characters)
    filename = pdf_path.name
    try:
        year = filename[:4]
        if not year.isdigit():
            raise ValueError(f"Could not extract year from filename: {filename}")
    except (IndexError, ValueError) as e:
        print(f"Warning: {e}. Using current year.")
        year = str(pd.Timestamp.now().year)
    
    records = []
    current = None
    
    # Skip patterns - lines that should be ignored
    skip_patterns = {
        "DATE",
        "DESCRIPTION",
        "AMOUNT",
        "BALANCE",
        "TRANSACTION DETAIL",
        "CHECKING SUMMARY",
        "SAVINGS SUMMARY",
        "Beginning Balance",
        "Ending Balance",
        "DEPOSITS AND ADDITIONS",
        "ATM & Debit Card Withdrawals",
        "Electronic Withdrawals",
        "Other Withdrawals",
        "Deposits and Additions",
        "Your account ending",
        "Page "
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                    
                lines = text.split("\n")
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Skip header/summary lines
                    if any(line.startswith(pattern) for pattern in skip_patterns):
                        continue
                    
                    # Check if this is a new transaction (starts with MM/DD date)
                    if DATE_RE.match(line):
                        # Save previous transaction
                        if current:
                            records.append(current)
                        
                        # Extract date (first 5 characters: MM/DD)
                        date = line[:5]
                        remainder = line[5:].strip()
                        
                        # Find all amounts in the line
                        amounts = AMOUNT_RE.findall(remainder)
                        
                        if len(amounts) >= 2:
                            # Normal case: last two amounts are transaction amount and balance
                            amount = amounts[-2]
                            balance = amounts[-1]
                            
                            # Description is text before the second-to-last amount
                            # Find position of second-to-last amount
                            desc_end = remainder.rfind(amount)
                            # But we need to find the second-to-last occurrence
                            temp = remainder[:desc_end]
                            if amount in temp:
                                desc_end = temp.rfind(amount)
                            description = remainder[:desc_end].strip()
                            
                        elif len(amounts) == 1:
                            # Only balance present (shouldn't happen often)
                            balance = amounts[0]
                            amount = "0.00"
                            desc_end = remainder.rfind(balance)
                            description = remainder[:desc_end].strip()
                            
                        else:
                            # No amounts found - incomplete line, description only
                            description = remainder
                            amount = ""
                            balance = ""
                        
                        current = {
                            "date": date,
                            "year": year,  # Store year from filename
                            "description": description,
                            "amount": amount,
                            "balance": balance,
                            "source_file": pdf_path.name,
                        }
                        
                    # Continuation line (description wraps to next line)
                    elif current:
                        # Check if this continuation line has amounts
                        amounts = AMOUNT_RE.findall(line)
                        
                        if amounts and not current["amount"]:
                            # Previous line didn't have amounts, they're on this line
                            if len(amounts) >= 2:
                                current["amount"] = amounts[-2]
                                current["balance"] = amounts[-1]
                                # Add any description text before the amounts
                                desc_end = line.rfind(amounts[-2])
                                desc_part = line[:desc_end].strip()
                                if desc_part:
                                    current["description"] += " " + desc_part
                            elif len(amounts) == 1:
                                current["balance"] = amounts[0]
                                desc_end = line.rfind(amounts[0])
                                desc_part = line[:desc_end].strip()
                                if desc_part:
                                    current["description"] += " " + desc_part
                        else:
                            # Pure description continuation
                            current["description"] += " " + line
            
            # Add final transaction
            if current:
                records.append(current)
    
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF {pdf_path}: {str(e)}")
    
    # Create DataFrame
    if not records:
        return pd.DataFrame(columns=["date", "description", "amount", "balance", "source_file"])
    
    df = pd.DataFrame(records)
    
    # Clean and convert data types
    df["description"] = df["description"].str.strip()
    
    # Combine MM/DD with year from filename to create complete date
    df["date_str"] = df["date"] + "/" + df["year"]
    df["date"] = pd.to_datetime(df["date_str"], format="%m/%d/%Y", errors="coerce")
    df = df.drop(columns=["date_str", "year"])  # Remove temporary columns
    
    # Handle amount conversion (remove commas, convert to float)
    df["amount"] = df["amount"].replace("", None)
    df["amount"] = pd.to_numeric(
        df["amount"].str.replace(",", ""), 
        errors="coerce"
    )
    
    df["balance"] = df["balance"].replace("", None)
    df["balance"] = pd.to_numeric(
        df["balance"].str.replace(",", ""), 
        errors="coerce"
    )
    
    return df


def parse_multiple_statements(pdf_paths: list[Path]) -> pd.DataFrame:
    """
    Parse multiple Chase statement PDFs and combine into single DataFrame.
    
    Args:
        pdf_paths: List of paths to Chase statement PDF files
        
    Returns:
        Combined DataFrame from all statements, sorted by date
    """
    all_dfs = []
    
    for path in pdf_paths:
        try:
            df = parse_chase_statement(path)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            print(f"Warning: Skipped {path.name} due to error: {e}")
            continue
    
    if not all_dfs:
        return pd.DataFrame(columns=["date", "description", "amount", "balance", "source_file"])
    
    combined = pd.concat(all_dfs, ignore_index=True)
    
    # Sort by date (handling NaT values)
    combined = combined.sort_values("date", na_position="last").reset_index(drop=True)
    
    return combined


# Example usage
if __name__ == "__main__":
    # Define the path to raw statements
    statements_dir = Path(r"W:\PFRE\PFRE\data\raw")
    
    # Get all PDF files
    pdf_files = list(statements_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {statements_dir}")
    else:
        print(f"Found {len(pdf_files)} PDF files")
        
        # Parse all statements
        combined_df = parse_multiple_statements(pdf_files)
        
        if combined_df.empty:
            print("No transactions extracted")
        else:
            print(f"\nExtracted {len(combined_df)} transactions")
            print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
            
            # Save to CSV
            output_path = statements_dir.parent / "processed" / "all_transactions.csv"
            output_path.parent.mkdir(exist_ok=True)
            combined_df.to_csv(output_path, index=False)
            print(f"\nSaved to: {output_path}")
            
            # Display summary
            print("\nSample transactions:")
            print(combined_df.head(10))