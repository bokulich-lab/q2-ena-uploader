import ftplib
import qiime2
import os 
import pandas as pd
from q2_types.per_sample_sequences import \
    (CasavaOneEightSingleLanePerSampleDirFmt)


def transfer_files_to_ena(
            demux: CasavaOneEightSingleLanePerSampleDirFmt

)  -> qiime2.Metadata:
    ftp_host = 'webin2.ebi.ac.uk'
    username = os.getenv('ENA_USERNAME')
    password = os.getenv('ENA_PASSWORD')        

        
    df = demux.manifest
    metadata = []
    try:
        ftp = ftplib.FTP(ftp_host)
        ftp.login(user=username, passwd=password)
        ftp.dir()

        for row in df.itertuples(index=True, name ='Pandas'):  
            sampleid = row.Index

            file_forward = row.forward 
            if os.path.isfile(file_forward):
                filename = file_forward.split('/')[-1]
                ftp.delete(filename)
                try:
                    with open(file_forward, 'rb') as file:
                        ftp.storbinary(f'STOR {filename}', file)
                    metadata.append((sampleid,filename,True))
                except ftplib.all_errors as e:
                    metadata.append((sampleid,filename, False))    

            if row.reverse:
                file_reverse = row.reverse
                if os.path.isfile(file_reverse):
                    filename = file_reverse.split('/')[-1]
                    ftp.delete(filename)
                    try:
                        with open(file_reverse, 'rb') as file:
                            ftp.storbinary(f'STOR {filename}', file)
                        metadata.append((sampleid,filename,True))
                    except ftplib.all_errors as e:
                        metadata.append((sampleid,filename,False))    


        ftp.retrlines('LIST')
        ftp.quit()

    except ftplib.all_errors as e:
        raise RuntimeError(f"An error occurred during the FTP upload: {e}")
    
    upload_metadata = pd.DataFrame(metadata, columns=['sampleid','filename', 'status'])
    upload_metadata.set_index('sampleid', inplace=True)
    upload_metadata['status'] = upload_metadata['status'].astype(int)


    return qiime2.Metadata(upload_metadata)

