# Seafloor Reconstruction

## Project Structure

```text
.
├── data/                         # not included in this repository
│   ├── images/                   # SONAR PNG images
│   ├── gps/
│   │   └── fix.csv
│   ├── imu/
│   │   └── imu.csv
│   └── sonar_transform/
│       ├── range.json
│       └── bearing.json
├── src/                          # Python source code
├── environment.yml               # Conda environment
├── README.md
└── .gitignore
```

## Notes

The `data/` folder is excluded from GitHub via `.gitignore`.

To reproduce the results, the dataset must be placed locally using the folder structure shown above.
