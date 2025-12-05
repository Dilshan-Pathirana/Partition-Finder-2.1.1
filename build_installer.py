"""
Build script for creating PartitionFinder standalone installer
Requires: PyInstaller, Inno Setup (for Windows installer)
"""
import subprocess
import sys
import os
import shutil

def install_pyinstaller():
    """Install PyInstaller if not present"""
    print("📦 Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✅ PyInstaller installed\n")

def build_executable():
    """Build the standalone executable"""
    print("🔨 Building standalone executable...")
    print("This may take several minutes...\n")
    
    # Check if spec file exists
    if not os.path.exists("partfinder_gui.spec"):
        print("❌ Error: partfinder_gui.spec not found!")
        print("Creating spec file...")
        print("\n⚠️ Please run the build script again after spec file is created.")
        return False
    
    # Build using spec file
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "partfinder_gui.spec",
        "--clean",
        "--noconfirm"
    ])
    
    if result.returncode == 0:
        print("\n✅ Executable built successfully!")
        print("📁 Location: dist/PartitionFinder/")
        
        # Copy README.txt to dist folder
        if os.path.exists("dist/README.txt"):
            shutil.copy("dist/README.txt", "dist/PartitionFinder/README.txt")
            print("📄 Added README.txt to package")
        
        return True
    else:
        print("\n❌ Build failed!")
        return False

def create_portable_package():
    """Create a portable ZIP package"""
    print("\n📦 Creating portable package...")
    
    dist_folder = "dist/PartitionFinder"
    zip_name = "PartitionFinder-2.1.1-Python3-Portable"
    
    if os.path.exists(dist_folder):
        shutil.make_archive(zip_name, 'zip', 'dist', 'PartitionFinder')
        print(f"✅ Portable package created: {zip_name}.zip")
        return True
    return False

def main():
    """Main build process"""
    print("=" * 70)
    print("   PartitionFinder 2.1.1 - Build Standalone Installer")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Install PyInstaller
        install_pyinstaller()
        
        # Step 2: Build executable
        if not build_executable():
            sys.exit(1)
        
        # Step 3: Create portable package
        create_portable_package()
        
        print("\n" + "=" * 70)
        print("✅ BUILD COMPLETE!")
        print("=" * 70)
        print("\n📂 Output Files:")
        print("   • dist/PartitionFinder/           - Executable folder")
        print("   • PartitionFinder-2.1.1-Python3-Portable.zip - Portable package")
        print("\n🚀 To distribute:")
        print("   1. Share the .zip file")
        print("   2. Users extract and run PartitionFinder.exe")
        print("   3. No Python installation needed!")
        
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
