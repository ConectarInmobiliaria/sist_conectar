#define MyAppName "Sistema Conectar Inmobiliaria"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Conectar Inmobiliaria"
#define MyAppURL "https://github.com/ConectarInmobiliaria/sist_conectar"
#define MyAppExeName "SistemaConectar.exe"

[Setup]
AppId={{8F3D4E2A-9B5C-4F1E-A7D3-2C8E9F6B1A4D}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\SistemaConectar
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=SistemaConectar_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=imagenes\favicon.png
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: checkedonce

[Files]
Source: "dist\SistemaConectar.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "imagenes\*"; DestDir: "{app}\imagenes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "inmobiliaria.db"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\recibos"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\recibos"