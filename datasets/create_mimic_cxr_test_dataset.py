import pandas as pd
import argparse


def generate_csv(metadata_path, records_path, studies_path, labels_path, disease, seed, n_samples, batch_name, use_processed, output_csv):
    # Load dataframes
    metadata_df = pd.read_csv(metadata_path)
    records_df = pd.read_csv(records_path)
    studies_df = pd.read_csv(studies_path)
    labels_df = pd.read_csv(labels_path)
    
    # Extract batch name from study path
    studies_df.rename(columns = {'path': 'report_path'}, inplace = True)
    studies_df['batch'] = studies_df['report_path'].apply(lambda x: x.split('/')[1])
    
    # Filter metadata to include only PA view and matching batch
    metadata_filtered = metadata_df[metadata_df['ViewPosition'] == 'PA']
    #metadata_filtered = metadata_df
    
    # Merge metadata with studies_df to get batch info
    metadata_filtered = metadata_filtered.merge(studies_df[['study_id', 'batch', 'report_path']], on='study_id', how='inner')
    metadata_filtered = metadata_filtered[metadata_filtered['batch'] == batch_name]
    
    # Merge with labels_df to get disease labels
    filtered_df = metadata_filtered.merge(labels_df[['study_id', disease]], on='study_id', how='inner')
    filtered_df = filtered_df[filtered_df[disease].isin([0, 1])] #-1 means uncertainty and will be excluded 
    
    # Merge with records_df to get image paths
    records_df.rename(columns = {'path': 'record_path'}, inplace = True)
    final_df = filtered_df.merge(records_df[['subject_id', 'study_id', 'dicom_id', 'record_path']], on=['subject_id', 'study_id', 'dicom_id'], how='inner')
    
    # Merge to get report paths
    #final_df = final_df.merge(studies_df[['study_id', 'report_path']], on='study_id', how='inner')
    final_df.rename(columns={disease: 'label'}, inplace=True)
    
    # Sample rows
    final_df = final_df.sample(n=min(n_samples, len(final_df)), random_state=seed)
    print(final_df.columns)
    
    # Modify record paths
    if use_processed:
        def edit_path(path):
            path = '/'.join(path.split('/')[1:])
            path = path.split('/')[0] + '_processed/' + '/'.join(path.split('/')[1:])
            path = path.replace('.dcm', '.jpg')
            return path
            
        final_df['record_path'] = final_df['record_path'].apply(edit_path)

    # Save to CSV
    final_df[['study_id', 'dicom_id', 'record_path', 'report_path', 'label']].to_csv(output_csv, index=False)
    print(f'Total studies: {final_df.study_id.nunique()}')
    print(f'Total records: {len(final_df)}')
    print(f'{final_df.label.value_counts()}')
    print(f"CSV saved to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a CSV file from MIMIC-CXR dataset.")
    parser.add_argument("--metadata_path", type=str, default = '/Users/juanpablomeli/Documents/personal/Tesis/MIMIC-CXR/MIMIC-CXR-JPG/mimic-cxr-2.0.0-metadata.csv' , help="Path to metadata CSV")
    parser.add_argument("--records_path", type=str, default = '/Users/juanpablomeli/Documents/personal/Tesis/MIMIC-CXR/cxr-record-list.csv', help="Path to records CSV")
    parser.add_argument("--studies_path", type=str, default = '/Users/juanpablomeli/Documents/personal/Tesis/MIMIC-CXR/cxr-study-list.csv', help="Path to studies CSV")
    parser.add_argument("--labels_path", type=str, default = '/Users/juanpablomeli/Documents/personal/Tesis/MIMIC-CXR/MIMIC-CXR-JPG/mimic-cxr-2.1.0-test-set-labeled.csv', help="Path to labels CSV, with ground truths. Use this csv as the set of records to filter.")
    parser.add_argument("--disease", type=str, required=True, help="Disease name")
    parser.add_argument("--seed", type=int, default = 42, help="Seed for random sampling")
    parser.add_argument("--n_samples", type=int, default = 300, help="Number of samples")
    parser.add_argument("--batch_name", type=str, default = 'p19', help="Batch name")
    parser.add_argument("--use_processed_images", type=bool, default = True, help="If true use processed jpg images")
    parser.add_argument("--output_csv", type=str, required=True, help="Output CSV path")
    
    args = parser.parse_args()
    
    generate_csv(
        args.metadata_path, args.records_path, args.studies_path,
        args.labels_path, args.disease, args.seed, args.n_samples,
        args.batch_name, args.use_processed_images, args.output_csv
    )
