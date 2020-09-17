import re
from pathlib import Path
import hashlib
import json
import datetime

import requests
from tqdm import tqdm


variants = [
    {
        "name": "x86_64",
        "version":
        {
            "url" : "https://jenkins.simonrichter.eu/job/windows-kicad-msys2-pipeline/lastSuccessfulBuild/artifact/pack-x86_64/",
            "re"  : "kicad-r([\\d]+\\.[a-f0-9]+)-x86_64\\.exe"
        },
        "download":
        {
            "url" : "https://kicad-downloads.s3.cern.ch/windows/nightly/kicad-r{version}-x86_64.exe"
        }
    },
    {
        "name": "x86_64-lite",
        "version":
        {
            "url" : "https://jenkins.simonrichter.eu/job/windows-kicad-msys2-pipeline/lastSuccessfulBuild/artifact/pack-x86_64/",
            "re"  : "kicad-r([\\d]+\\.[a-f0-9]+)-x86_64-lite\\.exe"
        }
        ,
        "download":
        {
            "url" : "https://kicad-downloads.s3.cern.ch/windows/nightly/kicad-r{version}-x86_64-lite.exe"
        }
    },
    {
        "name": "i686",
        "version":
        {
            "url" : "https://jenkins.simonrichter.eu/job/windows-kicad-msys2-pipeline/lastSuccessfulBuild/artifact/pack-i686/",
            "re"  : "kicad-r([\\d]+\\.[a-f0-9]+)-i686\\.exe"
        },
        "download":
        {
            "url" : "https://kicad-downloads.s3.cern.ch/windows/nightly/kicad-r{version}-i686.exe"
        }
    },
    {
        "name": "i686-lite",
        "version":
        {
            "url" : "https://jenkins.simonrichter.eu/job/windows-kicad-msys2-pipeline/lastSuccessfulBuild/artifact/pack-i686/",
            "re"  : "kicad-r([\\d]+\\.[a-f0-9]+)-i686-lite\\.exe"
        },
        "download":
        {
            "url" : "https://kicad-downloads.s3.cern.ch/windows/nightly/kicad-r{version}-i686-lite.exe"
        }
    }
]


def run_hash():
    file_hashes = []
    for variant in variants:
        response = requests.get(variant['version']['url'])

        version = re.search(variant['version']['re'], response.text)

        if version is not None:
            version = version.groups()[0]
        else:
            print(f'Variant not found, skipping: (Variant: {variant["name"]}')
            continue
        
        artifact = download_file(variant['download']['url'].format(version=version))
        hashes = hash_file(artifact)
        file_hashes.append({
            "variant": variant['name'],
            "download" : variant['download']['url'].format(version=version),
            "hashes": hashes
        })

        artifact.unlink()
    
    checksum_dir = Path('checksums')
    checksum_dir.mkdir(parents=True, exist_ok=True)
    
    with Path(f'{checksum_dir}/kicad.json').open(mode='wt') as jfile:
        file_hashes['updated'] = datetime.datetime.now().isoformat()
        json.dump(file_hashes, jfile)
    


def download_file(url):
    file_path = Path(f'downloads/{url.split("/")[-1]}')
    file_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_size=2**16
 
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        size = int(r.headers.get('content-length', 0))
        print(f'Downloading to: {file_path.resolve()}')
        progress_bar = tqdm(total=size, unit='iB', unit_scale=True)

        with file_path.open(mode='wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                progress_bar.update(len(chunk))
                f.write(chunk)
        progress_bar.close()

    return file_path


def hash_file(file):
    """Generates a list of hashes for the provided file

    Args:
        file (Path): Path object to the file to be hashed
    """
    chunksize = 2**16

    hashes_algos = [
        "sha1",
        "sha256",
        "sha512",
        "md5"
    ]

    hashes = {}

    with file.open(mode='rb') as f:
        for algo in hashes_algos:
            f.seek(0)
            m = hashlib.new(algo)

            chunk = f.read(chunksize)
            while len(chunk) > 0:
                m.update(chunk)
                chunk = f.read(chunksize)

            hashes[algo] = m.hexdigest()
    
    return hashes


run_hash()
