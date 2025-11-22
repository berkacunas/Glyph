; -- Glyph_Installer.iss --
; Inno Setup Script for Glyph Markdown Editor

#define MyAppName "Glyph"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Berk Acunas"
#define MyAppURL "https://github.com/berkacunas/Glyph"
#define MyAppExeName "Glyph.exe"
#define MyAppIcon "src\assets\icons\markdown.ico"

[Setup]
; --- General Settings ---
AppId={{C8D23984-0923-4B82-9123-GLYPH123456}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Default Installation Folder: C:\Program Files\Glyph
DefaultDirName={autopf}\{#MyAppName}
; Start Menu Folder Name
DefaultGroupName={#MyAppName}

; License File (shown in Setup)
LicenseFile=LICENSE
; Image to appear on the left of the installation (Optional, disabled for now)
; WizardImageFile=installer_bg.bmp

; Output Settings (Where will the installer be created?)
OutputDir=dist\installer
OutputBaseFilename=Glyph_Setup_v{#MyAppVersion}
SetupIconFile={#MyAppIcon}

; Compression Settings (Best)
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; CRITICAL SECTION: COPYING FILES
; Take everything in the 'dist/Glyph' folder created with PyInstaller.
; Flags: ignoreversion recursesubdirs createallsubdirs -> Get subfolders too.
Source: "dist\Glyph\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; (Put the README file in the main directory, although it is already in dist/Glyph, just to be sure)
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\markdown.ico"
; Desktop Shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\icons\markdown.ico"
; Uninstall Shortcut
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Run]
; Once the installation is complete, select "Run the Program"
; Filename: "{commondesktop}\{#MyAppName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent