# Clear the Client Cache ON FILEMAKER PRO

Utilizzato quando

Corrupted temporary cache files on your local machine are the most common cause of table loading errors. [[1](https://cabitas.com/en/blog/tablemissing-error-in-all-fields-and-solution)]

**On macOS:**

1. Quit FileMaker Pro completely.
2. Open Finder, hold down `Command + Shift + G`.
3. Paste `~/Library/Caches/FileMaker/DBCache/` and click Go.
4. Move all folders inside the `DBCache` directory to the Trash.
5. Empty the Trash and restart FileMaker. [[1](https://community.claris.com/en/s/question/0D50H00006ezLdXSAU/field-missing-appears-instead-of-field-data)]

**On Windows:**

1. Quit FileMaker Pro completely.
2. Open File Explorer and navigate to the temp folder by typing `%localappdata%\Temp` in the address bar.
3. Open the **FileMaker** folder.
4. Delete the subfolders located here (such as `ContainerCache`, `DBCache`, or `DBFileThumbnails`).