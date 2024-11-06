from cx_Freeze import setup, Executable

setup(
    name="IndoorMapper",
    version="1.0",
    description="Convert KML to KMZ",
    executables=[Executable("IndoorMapper.py")]
)
