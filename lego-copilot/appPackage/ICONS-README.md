# App Package Icons

This directory should contain the following icon files for the Teams app:

## Required Icons

### 1. color.png
- **Size**: 192x192 pixels
- **Format**: PNG
- **Purpose**: Full color icon displayed in Teams app gallery
- **Design**: Should be eye-catching and represent your LEGO bot
- **Suggestions**: 
  - Use LEGO brick colors (red, blue, yellow)
  - Include robot or LEGO-related imagery
  - Ensure good contrast and visibility

### 2. outline.png
- **Size**: 32x32 pixels
- **Format**: PNG with transparent background
- **Purpose**: Monochrome outline icon used in Teams UI
- **Design**: Simple, clear outline that works in light and dark themes
- **Suggestions**:
  - Simple line art or silhouette
  - Single color (typically white on transparent)
  - Must be recognizable at small size

## Creating Icons

You can create these icons using:

- **Online Tools**: 
  - [Canva](https://www.canva.com/) - Easy drag-and-drop design
  - [Figma](https://www.figma.com/) - Professional design tool
  - [favicon.io](https://favicon.io/) - Quick icon generator

- **Design Software**:
  - Adobe Photoshop
  - Adobe Illustrator
  - GIMP (free alternative)

- **Quick Solution**:
  - Use any square image and resize to 192x192 and 32x32
  - Ensure PNG format with transparency where needed

## Validation

Before packaging, verify:
- ✅ Both files are named exactly `color.png` and `outline.png`
- ✅ Dimensions are correct (192x192 and 32x32)
- ✅ Files are PNG format
- ✅ Files are in the `appPackage` directory

## Note

Without these icons, the Teams app package will not be valid and cannot be uploaded to Teams. Create or add these files before running the packaging script.
