# Hasher

This script is generates a set of checksums for any http(s) downloadable file  
The files to hash are listed in a dictionary as variants, with a url to regex for the version, and a url to insert the version into for downloads.

This seperation of version/download url allows the script to find the version on a build server, but download from a CDN, as long as the version naming is consistent between the two.

Several variants can be provided, and a list of hashes will be generated for each variant. The output is stored in checksums.json (which has been beutified for this repo, but is normally minified)

The original intention was to have any artifact described by a json manifest (and that might still happen) however for once I grabbed myself in the act of trying to write a framework for a one-off script. If I find I need the framework in the future I still have the work I did on that :)

Running hasher.py does it all for now :)