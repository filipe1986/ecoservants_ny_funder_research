import pandas as pd

def filter_irs_master_file(input_file_path, output_file_path):
    # loading the IRS datafile
    # works with csv, change to pd.read_excel if it is an xlsx file
    df = pd.read_csv(input_file_path)

    # Strict keyword lists from the Step 1 guidelines
    funder_keywords = [
        "FOUNDATION", "FAMILY FOUNDATION", "CHARITABLE FOUNDATION", "TRUST", "FUND", "COMMUNITY FOUNDATION", "ENDOWMENT"
    ]

    mission_keywords = [
        "ENVIRONMENTAL", "CONSERVATION", "EDUCATION", "YOUTH DEVELOPMENT", 
        "COMMUNITY IMPROVEMENT", "PUBLIC BENEFIT", "SUSTAINABILITY", "VOLUNTEER"
    ]

    # converting company names to uppercase to ensure accurate matching
    # assuming the column containing names is called 'NAME' or 'ORGANIZATION_NAME'
    df['NAME_UPPER'] = df['NAME'].astype(str).str.upper()

    # Apply the logical filter matrix
    # matches rows that contain at least one funder keyword or one misson keyword
    funder_mask = df['NAME_UPPER'].str.contains('|'.join(funder_keywords), na=False)

    mission_mask = df['NAME_UPPER'].str.contains('|'.join(mission_keywords), na=False)

    filtered_df = df[funder_mask | mission_mask]

    # drop the temporary helper colum before saving
    filtered_df = filtered_df.drop(columns=['NAME_UPPER'])

    # export the prioritized prospects cleanly
    filtered_df.to_csv(output_file_path, index=False)

    print(f'Step 1 complete! Saved {len(filtered_df)} prioritized prospects to {output_file_path}')

    #  --- execution entry point --- 

