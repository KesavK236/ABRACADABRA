; Inno Setup 6 script for ABRACADABRA.
;
; 1. pyinstaller main.spec --clean --noconfirm
; 2. (release builds) sign every .exe/.dll/.pyd under dist\ABRACADABRA
; 3. ISCC.exe installer\ABRACADABRA.iss      -> installer\Output\ABRACADABRA-Setup-<ver>.exe
;    Override the version with: ISCC.exe /DAppVersion=1.2.3 installer\ABRACADABRA.iss
; 4. (release builds) sign the setup .exe
;
; Per-user install (no admin prompt) into %LOCALAPPDATA%\Programs\ABRACADABRA.
; The app writes its outputs and config.json to the current working directory,
; so shortcuts start it in Documents\ABRACADABRA instead of the install folder.

#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

#define AppName "ABRACADABRA"
#define AppExe  "ABRACADABRA.exe"

[Setup]
; Keep this AppId fixed across releases so upgrades replace the old install.
AppId={{6F3C2B1E-9A4D-4E7B-8C21-5D9A7E0B4F63}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=KesavK236
AppPublisherURL=https://github.com/KesavK236/ABRACADABRA
AppSupportURL=https://github.com/KesavK236/ABRACADABRA/issues
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=..\LICENSE
SetupIconFile=..\assets\ABRACADABRA.ico
UninstallDisplayIcon={app}\{#AppExe}
OutputDir=Output
OutputBaseFilename={#AppName}-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; SignTool=signtool $f   <- enable once a signing tool is configured in Inno Setup

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
Name: "{userdocs}\{#AppName}"; Flags: uninsneveruninstall

[Files]
Source: "..\dist\{#AppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; Clear the previous build's bundled libraries so stale files don't linger after upgrades.
Type: filesandordirs; Name: "{app}\_internal"

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{userdocs}\{#AppName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{userdocs}\{#AppName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; WorkingDir: "{userdocs}\{#AppName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
