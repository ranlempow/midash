
@set SCRIPT_SOURCE=%~f0
@set SCRIPT_FOLDER=%~dp0
@if "%SCRIPT_FOLDER:~-1%" == "\" @set SCRIPT_FOLDER=%SCRIPT_FOLDER:~0,-1%


::: function Main(cmd=shell,
:::                   args=...)
:Main
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_Main
:PCALL_Main
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_Main
set cmd=shell
set args=

:ArgCheckLoop_Main
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_Main
if "%next%" == "" set next=__NONE__

@if "%head%" == "--cmd" @(
    @set cmd=%next%
    @if "%next%" == "__NONE__" @endlocal & ( @set "ERROR_MSG=Need value after "%head%"" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=Main" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
    @if "%next:~0,1%" == "-" @endlocal & ( @set "ERROR_MSG=Need value after "%head%"" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=Main" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
    @shift
    @shift
    @goto :ArgCheckLoop_Main
)
@goto :GetRestArgs_Main

:GetRestArgs_Main

@set args="%~1"
@shift
:GetRestArgsLoop_Main
@if "%~1" == "" @goto :Main_Main
@set args=%args% "%~1"
@shift
@goto :GetRestArgsLoop_Main
:Main_Main
@set head=
@set next=
@set _devcmd=%cmd%
@set _devargs=%args%
@set cmd=
@set args=
@call :ExcuteCommand
endlocal
goto :eof



:SubString
    @if "%Text%" EQU "" goto :ENDSubString
    @for /f "delims=;" %%a in ("!Text!") do @set substring=%%a
    @call goto %LoopCb%
    @if not "%LoopBreak%" == "" goto :ENDSubString

:NextSubString
    @set headchar=!Text:~0,1!
    @set Text=!Text:~1!

    @if "!Text!" EQU "" goto :SubString
    @if "!headchar!" NEQ "%Spliter%" goto :NextSubString
    @goto :SubString

:ENDSubString
@set Text=
@set Spliter=
@set headchar=
@set substring=
@set LoopBreak=
@set LoopCb=
@(set ExitCb=)& call goto %ExitCb%
@goto :eof

:: 讀取ini檔案的方法, 將取得的值寫入%inival%
:: GetIniArray(file, area)
::   inival = "v1;v2"
:: GetIniPairs(file, area)
::   inival = "k1=v1;k2=v2"
:: GetIniValue(file, area, key)
::   inival = "v"

::: function GetIniArray(file, area) extensions delayedexpansion
:GetIniArray
@setlocal enableextensions enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_GetIniArray
:PCALL_GetIniArray
@setlocal enableextensions enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_GetIniArray
set file=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument file" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniArray" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set area=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument area" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniArray" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift

:ArgCheckLoop_GetIniArray
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_GetIniArray
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniArray" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_GetIniArray
:Main_GetIniArray
@set head=
@set next=
set inival=
if not exist "%file%" goto :return_GetIniArray
set area=[%area%]
set currarea=
for /f "usebackq delims=" %%a in ("!file!") do (
    set ln=%%a
    for /f "tokens=* delims= " %%a in ("!ln!") do set ln=%%a
    if not "x!ln!" == "x" (
        if "x!ln:~0,1!"=="x[" (
            set currarea=!ln!
        ) else (
            for /f "tokens=1,2 delims==" %%b in ("!ln!") do (
                set currkey=%%b
                set currval=%%c

                if "x!area!"=="x!currarea!" (
                    if "x!inival!" == "x" (
                        set "inival=!currkey!"
                    ) else (
                        set "inival=!inival!;!currkey!"
                    )
                )
            )
        )
    )
)
:return_GetIniArray
endlocal & (
    set inival=%inival%
)
goto :eof
endlocal
goto :eof

::: function GetIniPairs(file, area) extensions delayedexpansion
:GetIniPairs
@setlocal enableextensions enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_GetIniPairs
:PCALL_GetIniPairs
@setlocal enableextensions enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_GetIniPairs
set file=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument file" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniPairs" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set area=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument area" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniPairs" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift

:ArgCheckLoop_GetIniPairs
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_GetIniPairs
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniPairs" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_GetIniPairs
:Main_GetIniPairs
@set head=
@set next=
set inival=
if not exist "%file%" goto :return_GetIniPairs
set area=[%area%]
set currarea=
for /f "usebackq delims=" %%a in ("!file!") do (
    set ln=%%a
    for /f "tokens=* delims= " %%a in ("!ln!") do set ln=%%a
    if not "x!ln!" == "x" (
        if "x!ln:~0,1!"=="x[" (
            set currarea=!ln!
        ) else (
            for /f "tokens=1,2 delims==" %%b in ("!ln!") do (
                set currkey=%%b
                set currval=%%c

                if "x!area!"=="x!currarea!" (
                    if "x!inival!" == "x" (
                        set "inival=!currkey!=!currval!"
                    ) else (
                        set "inival=!inival!;!currkey!=!currval!"
                    )
                )
            )
        )
    )
)
:return_GetIniPairs
endlocal & (
    set inival=%inival%
)
goto :eof
endlocal
goto :eof

::: function GetIniValue(file, area, key) extensions delayedexpansion
:GetIniValue
@setlocal enableextensions enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_GetIniValue
:PCALL_GetIniValue
@setlocal enableextensions enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_GetIniValue
set file=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument file" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniValue" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set area=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument area" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniValue" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set key=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument key" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniValue" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift

:ArgCheckLoop_GetIniValue
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_GetIniValue
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=parseini.cmd" & @set "ERROR_BLOCK=GetIniValue" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_GetIniValue
:Main_GetIniValue
@set head=
@set next=
set inival=
if not exist "%file%" goto :return_GetIniValue
set area=[%area%]
set currarea=

for /f "usebackq delims=" %%a in ("!file!") do (
    set ln=%%a
    for /f "tokens=* delims= " %%a in ("!ln!") do set ln=%%a
    if not "x!ln!" == "x" (
        if "x!ln:~0,1!"=="x[" (
            set currarea=!ln!
        ) else (
            for /f "tokens=1,2 delims==" %%b in ("!ln!") do (
                set currkey=%%b
                set currval=%%c

                if "x!area!"=="x!currarea!" if "x!key!"=="x!currkey!" (
                    set inival=!currval!
                    goto :return_GetIniValue
                )
            )
        )
    )
)
:return_GetIniValue
endlocal & (
    set inival=%inival%
)
goto :eof
endlocal
goto :eof

::: function GetPrjRoot()
:GetPrjRoot
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_GetPrjRoot
:PCALL_GetPrjRoot
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_GetPrjRoot

:ArgCheckLoop_GetPrjRoot
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_GetPrjRoot
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=project-paths.cmd" & @set "ERROR_BLOCK=GetPrjRoot" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_GetPrjRoot
:Main_GetPrjRoot
@set head=
@set next=
call :get_dir %SCRIPT_SOURCE%
set PRJ_ROOT=
pushd %dir%
set PRJ_ROOT=%cd%
popd
endlocal & (
    set PRJ_ROOT=%PRJ_ROOT%
)
goto :eof
:get_dir
    set dir=%~dp0
goto :eof
endlocal
goto :eof

::: function GetTitle(titlePath)
:GetTitle
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_GetTitle
:PCALL_GetTitle
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_GetTitle
set titlePath=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument titlePath" & @set "ERROR_SOURCE=project-paths.cmd" & @set "ERROR_BLOCK=GetTitle" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift

:ArgCheckLoop_GetTitle
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_GetTitle
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=project-paths.cmd" & @set "ERROR_BLOCK=GetTitle" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_GetTitle
:Main_GetTitle
@set head=
@set next=
set SPLITSTR=%titlePath%
:nextVar
   for /F tokens^=1*^ delims^=^\ %%a in ("%SPLITSTR%") do (
      set LAST=%%a
      set SPLITSTR=%%b
   )
if defined SPLITSTR goto nextVar
set TITLE=%LAST%
endlocal & (
    set TITLE=%TITLE%
)
goto :eof
endlocal
goto :eof

::: function LoadConfigPaths()
:LoadConfigPaths
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_LoadConfigPaths
:PCALL_LoadConfigPaths
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_LoadConfigPaths

:ArgCheckLoop_LoadConfigPaths
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_LoadConfigPaths
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=project-paths.cmd" & @set "ERROR_BLOCK=LoadConfigPaths" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_LoadConfigPaths
:Main_LoadConfigPaths
@set head=
@set next=
:: 尋找並讀取devone.ini設定檔, 此檔案可以放在PRJ_ROOT或是PRJ_ROOT/config
:: 不論此設定檔存在與否, 均會回傳以下路徑設定
:: PRJ_BIN, PRJ_VAR, PRJ_LOG, PRJ_TMP, PRJ_CONF

call :GetPrjRoot
call :GetTitle %PRJ_ROOT%


set CONFIG_PATH=
pushd %PRJ_ROOT%
pushd config 2>nul
if not errorlevel 1 (
    if exist "devone.ini" set CONFIG_PATH=%cd%
    popd
)
if exist "devone.ini" set CONFIG_PATH=%cd%
popd
if not "%CONFIG_PATH%" == "" set DEVONE_CONFIG_PATH=%CONFIG_PATH%\devone.ini




call :GetIniValue %CONFIG_PATH%\devone.ini layout bin
set PRJ_BIN_RAW=%inival%
call :GetIniValue %CONFIG_PATH%\devone.ini layout var
set PRJ_VAR_RAW=%inival%
call :GetIniValue %CONFIG_PATH%\devone.ini layout log
set PRJ_LOG_RAW=%inival%
call :GetIniValue %CONFIG_PATH%\devone.ini layout tmp
set PRJ_TMP_RAW=%inival%
call :GetIniValue %CONFIG_PATH%\devone.ini layout config
set PRJ_CONF_RAW=%inival%

if "%PRJ_BIN_RAW%" == "" if exist "%PRJ_ROOT%\bin" set PRJ_BIN_RAW=bin
if "%PRJ_VAR_RAW%" == "" if exist "%PRJ_ROOT%\var" set PRJ_VAR_RAW=var
if "%PRJ_LOG_RAW%" == "" if exist "%PRJ_ROOT%\log" set PRJ_LOG_RAW=log
if "%PRJ_TMP_RAW%" == "" if exist "%PRJ_ROOT%\tmp" set PRJ_TMP_RAW=tmp
if "%PRJ_CONF_RAW%" == "" if exist "%PRJ_ROOT%\config" set PRJ_CONF_RAW=config


if "%PRJ_BIN_RAW%" == "" set PRJ_BIN_RAW=bin
set PRJ_BIN=%PRJ_ROOT%\%PRJ_BIN_RAW%
if "%PRJ_VAR_RAW%" == "" (
    set PRJ_VAR=%TEMP%\devone-%TITLE%
) else (
    set PRJ_VAR=%PRJ_ROOT%\%PRJ_VAR_RAW%
)
if "%PRJ_LOG_RAW%" == "" (
    set PRJ_LOG=%PRJ_VAR%\log
) else (
    set PRJ_LOG=%PRJ_ROOT%\%PRJ_LOG_RAW%
)
if "%PRJ_TMP_RAW%" == "" (
    set PRJ_TMP=%PRJ_VAR%\tmp
) else (
    set PRJ_TMP=%PRJ_ROOT%\%PRJ_TMP_RAW%
)
if "%PRJ_CONF_RAW%" == "" (
    if not "%CONFIG_PATH%" == "" set PRJ_CONF=%CONFIG_PATH%
) else (
    set PRJ_CONF=%PRJ_ROOT%\%PRJ_CONF_RAW%
)
if "%PRJ_CONF%" == "" set PRJ_CONF=%PRJ_ROOT%\config


endlocal & (
    set DEVONE_CONFIG_PATH=%DEVONE_CONFIG_PATH%
    set PRJ_ROOT=%PRJ_ROOT%
    set PRJ_BIN=%PRJ_BIN%
    set PRJ_VAR=%PRJ_VAR%
    set PRJ_LOG=%PRJ_LOG%
    set PRJ_TMP=%PRJ_TMP%
    set PRJ_CONF=%PRJ_CONF%
)
goto :eof
endlocal
goto :eof


::: inline(VAR)
::: endinline
::: function BasicCheck()
:BasicCheck
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_BasicCheck
:PCALL_BasicCheck
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_BasicCheck

:ArgCheckLoop_BasicCheck
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_BasicCheck
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=BasicCheck" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_BasicCheck
:Main_BasicCheck
@set head=
@set next=
if not "%~d0" == "C:" (
     @endlocal & ( @set "ERROR_MSG=folder must in C:" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
)
echo %~dp0| findstr /R /C:"^[a-zA-Z0-9~.\\:_-]*$">nul 2>&1
if errorlevel 1 (
     @endlocal & ( @set "ERROR_MSG=folder path contains illegal characters" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
)
endlocal
goto :eof


:ActiveDevShell
if not "%DEVSH_ACTIVATE%" == "" goto :eof

call :BasicCheck
call :LoadConfigPaths
call :GetTitle !PRJ_ROOT!

set PATH=!PRJ_BIN!;!PRJ_TOOLS!;!PATH!

call :GetIniArray %DEVONE_CONFIG_PATH% "path"
set PATH=!inival!;!PATH!

if "%HOME%" == "" set HOME=PRJ_ROOT/.home
set PROMPT=$C!TITLE!$F$S$P$G

rmdir /S /Q !PRJ_TMP!\command
md !PRJ_TMP!\command
set PATH=!PRJ_TMP!\command;!PATH!

set inival=
call :GetIniArray %DEVONE_CONFIG_PATH% "dotfiles"
(set Text=!inival!)&(set LoopCb=:call_dotfile)&(set ExitCb=:exit_call_dotfile)&(set Spliter=;)
goto :SubString
:call_dotfile
    if exist "!substring!.cmd" call call "!substring!.cmd"
    goto :NextSubString
:exit_call_dotfile
set inival=

if exist "%PRJ_CONF%\hooks\set-env.cmd" (
    call "%PRJ_CONF%\hooks\set-env.cmd"
)


call :GetIniPairs %DEVONE_CONFIG_PATH% "alias"
(set Text=!inival!)&(set LoopCb=:create_alias_file)&(set ExitCb=:exit_create_alias_file)&(set Spliter=;)
goto :SubString
:create_alias_file
    echo !substring!
    for /f "tokens=1,2 delims==" %%a in ("!substring!") do (
        set alias=%%a
        set alias_cmd=%%b
    )
    echo.cmd.exe /C "%alias_cmd%" > %PRJ_TMP%\command\%alias%.cmd
    goto :NextSubString
:exit_create_alias_file
set alias=
set alias_cmd=
set inival=

echo.@"%SCRIPT_SOURCE%" --cmd %%* > %PRJ_TMP%\command\dev.cmd

set DEVSH_ACTIVATE=1
goto :eof



::: function ExcuteCommand() delayedexpansion
:ExcuteCommand
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_ExcuteCommand
:PCALL_ExcuteCommand
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_ExcuteCommand

:ArgCheckLoop_ExcuteCommand
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_ExcuteCommand
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=ExcuteCommand" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_ExcuteCommand
:Main_ExcuteCommand
@set head=
@set next=
:: 如果還沒進入shell則先進入臨時性的shell
call :ActiveDevShell
call :CMD_%_devcmd% %_devargs%
endlocal
goto :eof


::: function CMD_shell(no_window=N, no_welcom=N, args=...) delayedexpansion
:CMD_shell
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_CMD_shell
:PCALL_CMD_shell
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_CMD_shell
set no_window=0
set no_welcom=0
set args=

:ArgCheckLoop_CMD_shell
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_CMD_shell
if "%next%" == "" set next=__NONE__

@if "%head%" == "--no-window" @(
    @set no_window=1
    @shift
    @goto :ArgCheckLoop_CMD_shell
)
@if "%head%" == "--no-welcom" @(
    @set no_welcom=1
    @shift
    @goto :ArgCheckLoop_CMD_shell
)
@goto :GetRestArgs_CMD_shell

:GetRestArgs_CMD_shell

@set args="%~1"
@shift
:GetRestArgsLoop_CMD_shell
@if "%~1" == "" @goto :Main_CMD_shell
@set args=%args% "%~1"
@shift
@goto :GetRestArgsLoop_CMD_shell
:Main_CMD_shell
@set head=
@set next=
set CMDSCRIPT=
set CMDSCRIPT=!CMDSCRIPT!(set cmd_args=)^&(set cmd_executable=)^&(set command=)^&(set CMDSCRIPT=)^&

if "%no_welcom%" == "1" goto :no_welcome_text
set welcome1=Devone v1.0.0 [project !TITLE!]
set CMDSCRIPT=!CMDSCRIPT!(echo.!welcome1!)^&
set welcome1=
call :GetIniValue %DEVONE_CONFIG_PATH% "help" "*"
if not "!inival!" == "" set CMDSCRIPT=!CMDSCRIPT!(echo.!inival!)^&
set inival=
:no_welcome_text


where ansicon.exe 2> nul
if not errorlevel 1 (
    set cmd_executable=ansicon.exe %ComSpec%
) else (
    set cmd_executable=%ComSpec%
)

where clink.bat 2> nul
if not errorlevel 1 (
    set CMDSCRIPT=!CMDSCRIPT!clink.bat inject
)

set cmd_args=/K "!CMDSCRIPT!"
pushd %PRJ_ROOT%
echo on
@if "%no_window%" == "1" @(
    @%cmd_executable% %cmd_args%
) else @(
    @start "[%TITLE%]" %cmd_executable% %cmd_args%
)
@echo off
popd
endlocal
goto :eof

::: function CMD_setup(UserName=?, GithubToken=?)
:CMD_setup
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_CMD_setup
:PCALL_CMD_setup
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_CMD_setup
set UserName=
set GithubToken=

:ArgCheckLoop_CMD_setup
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_CMD_setup
if "%next%" == "" set next=__NONE__

@if "%head%" == "--username" @(
    @set UserName=%next%
    @if "%next%" == "__NONE__" @endlocal & ( @set "ERROR_MSG=Need value after "%head%"" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=CMD_setup" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
    @if "%next:~0,1%" == "-" @endlocal & ( @set "ERROR_MSG=Need value after "%head%"" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=CMD_setup" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
    @shift
    @shift
    @goto :ArgCheckLoop_CMD_setup
)
@if "%head%" == "--githubtoken" @(
    @set GithubToken=%next%
    @if "%next%" == "__NONE__" @endlocal & ( @set "ERROR_MSG=Need value after "%head%"" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=CMD_setup" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
    @if "%next:~0,1%" == "-" @endlocal & ( @set "ERROR_MSG=Need value after "%head%"" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=CMD_setup" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
    @shift
    @shift
    @goto :ArgCheckLoop_CMD_setup
)

 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=CMD_setup" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_CMD_setup
:Main_CMD_setup
@set head=
@set next=


for /f %%i in ('git config --local user.name') do set AlreadySetup=%%i
if not "%AlreadySetup%" == "" (
endlocal
goto :eof
)

git rev-parse 1>nul 1>&2
if errorlevel 1  @endlocal & ( @set "ERROR_MSG=Not a git repository" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )

if "%UserName%" == "" set /P UserName=Enter your name (or input 'global' use global config):
if "%GithubToken%" == "" set /P GithubToken=Enter the secret token:

for /f "tokens=1,2 delims==" %%a in ("%GithubToken%") do (
    set LoginName=%%a
    set LoginPassword=%%b
)

if "%UserName%" == ""  @endlocal & ( @set "ERROR_MSG=User name undefined" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
if "%LoginName%" == ""  @endlocal & ( @set "ERROR_MSG=Login name undefined" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
if "%LoginPassword%" == ""  @endlocal & ( @set "ERROR_MSG=Login password undefined" & @set "ERROR_SOURCE=CMD_setup.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )

if not exist "%HOME%" mkdir "%HOME%"

echo.machine github.com>> %HOME%/_netrc
echo.login %LoginName%>> %HOME%/_netrc
echo.password %LoginPassword%>> %HOME%/_netrc
echo.>> %HOME%/_netrc

echo.machine api.github.com>> %HOME%/_netrc
echo.login %LoginName%>> %HOME%/_netrc
echo.password %LoginPassword%>> %HOME%/_netrc
echo.>> %HOME%/_netrc

if not "%UserName%" == "global" (
	git config --local user.name %UserName%
	git config --local user.email %UserName%@users.noreply.github.com
	git config --local core.autocrlf true
	git config --local push.default simple
)

endlocal
goto :eof


::: function CMD_sync(MOST_CLEAN=N) delayedexpansion
:CMD_sync
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_CMD_sync
:PCALL_CMD_sync
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_CMD_sync
set MOST_CLEAN=0

:ArgCheckLoop_CMD_sync
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_CMD_sync
if "%next%" == "" set next=__NONE__

@if "%head%" == "--most-clean" @(
    @set MOST_CLEAN=1
    @shift
    @goto :ArgCheckLoop_CMD_sync
)

 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=CMD_sync.cmd" & @set "ERROR_BLOCK=CMD_sync" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_CMD_sync
:Main_CMD_sync
@set head=
@set next=





set MAIN_BRANCH=master
set CURRENT_CHANGES=
for /f %%i in ('git status --porcelain') do set CURRENT_CHANGES=%%i
for /f %%i in ('git symbolic-ref -q --short HEAD') do set CURRENT_BRANCH=%%i

if "%MOST_CLEAN%" == "1" if not "%CURRENT_CHANGES%" == ""  @endlocal & ( @set "ERROR_MSG=status most clean" & @set "ERROR_SOURCE=CMD_sync.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
if not "%CURRENT_CHANGES%" == "" git stash --include-untracked
if not "%CURRENT_BRANCH%" == "%MAIN_BRANCH%" git checkout %MAIN_BRANCH%

git fetch origin --progress
if errorlevel 1  @endlocal & ( @set "ERROR_MSG=cannot fetch, maybe your network is offline" & @set "ERROR_SOURCE=CMD_sync.cmd" & @set "ERROR_BLOCK=" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )


for /f %%i in ('git merge-base FETCH_HEAD %MAIN_BRANCH%') do set CommonCommit=%%i
git format-patch %CommonCommit%..FETCH_HEAD --stdout > .patchtest

for /f %%i in (".patchtest") do set filesize=%%~zi
if "%filesize%" == "0" (
    call :PrintMsg normal gitsync no change
    del .patchtest
    goto :return_CMD_sync
)

git apply --check .patchtest 2>nul
set errorlevel_save=%errorlevel%
del .patchtest

if "%errorlevel_save%" == "0" (
	call :PrintMsg normal gitsync fast forward
  	git merge -v FETCH_HEAD --ff-only
  	if not "!errorlevel!" == "0" (
	    call :PrintMsg normal gitsync rebase
	    git rebase FETCH_HEAD
  	)
) else (
	call :PrintMsg normal gitsync merge ours
	git merge -v FETCH_HEAD -s recursive -Xours
)

if not errorlevel 1 (
    git push -v origin --progress --tags
) else (
	call :PrintMsg error gitsync merge failed, this is a very rare situation
)

:return_CMD_sync
if not "%CURRENT_BRANCH%" == "%MAIN_BRANCH%" git checkout %CURRENT_BRANCH%
if not "%CURRENT_BRANCH%" == "%MAIN_BRANCH%" git rebase %MAIN_BRANCH%
if errorlevel 1 (
    call :PrintMsg warning gitsync rebase maybe conflict, abort rebase
    git rebase --abort
)
if not "%CURRENT_CHANGES%" == "" git stash pop

git submodule foreach git diff-index --quiet HEAD
if errorlevel 1 (
    call :PrintMsg warning gitsync some submodules is in the dirty status
    call :PrintMsg warning gitsync all submodules will not update until their folder is clean
) else (
	git submodule sync
	git submodule update --init --recursive
)

endlocal
goto :eof

::: function PreparePrint(PRINT_LEVEL, MSG_TITLE)
:PreparePrint
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_PreparePrint
:PCALL_PreparePrint
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_PreparePrint
set PRINT_LEVEL=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument PRINT_LEVEL" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PreparePrint" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set MSG_TITLE=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument MSG_TITLE" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PreparePrint" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift

:ArgCheckLoop_PreparePrint
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_PreparePrint
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PreparePrint" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_PreparePrint
:Main_PreparePrint
@set head=
@set next=
if "%THISNAME%" == "" set THISNAME=brickv

if "%PRINT_LEVEL%" == "error" set PRINT_LEVEL=5
if "%PRINT_LEVEL%" == "warning" set PRINT_LEVEL=4
if "%PRINT_LEVEL%" == "normal" set PRINT_LEVEL=3
if "%PRINT_LEVEL%" == "info" set PRINT_LEVEL=2
if "%PRINT_LEVEL%" == "debug" set PRINT_LEVEL=1

if "%LOG_LEVEL%" == "" set LOG_LEVEL=3

set MSG_TITLE_F="%MSG_TITLE%              "
set MSG_TITLE_F=%MSG_TITLE_F:~1,15%
if "%TEST_SHELL%" == "1" set MSG_TITLE_F=%MSG_TITLE%

endlocal & (
    set PRINT_LEVEL=%PRINT_LEVEL%
    set LOG_LEVEL=%LOG_LEVEL%
    set THISNAME=%THISNAME%
    set MSG_TITLE_F=%MSG_TITLE_F%
)
goto :eof
endlocal
goto :eof
::: function PrintMsg(PRINT_LEVEL, MSG_TITLE, MSG_BODY=....)
:PrintMsg
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_PrintMsg
:PCALL_PrintMsg
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_PrintMsg
set PRINT_LEVEL=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument PRINT_LEVEL" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintMsg" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set MSG_TITLE=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument MSG_TITLE" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintMsg" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set MSG_BODY=

:ArgCheckLoop_PrintMsg
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_PrintMsg
if "%next%" == "" set next=__NONE__

@goto :GetRestArgs_PrintMsg

:GetRestArgs_PrintMsg

@set MSG_BODY=%1
@shift
:GetRestArgsLoop_PrintMsg
@if "%~1" == "" @goto :Main_PrintMsg
@set MSG_BODY=%MSG_BODY% %1
@shift
@goto :GetRestArgsLoop_PrintMsg
:Main_PrintMsg
@set head=
@set next=
call :PreparePrint "%PRINT_LEVEL%" "%MSG_TITLE%"
call :ImportColor
set RedText=0
if "%MSG_TITLE%" == "error" set RedText=1
if "%MSG_TITLE%" == "warning" set RedText=1

if "%RedText%" == "1" (
    set OUTPUT=%THISNAME% %BR%%MSG_TITLE_F%%NN% %MSG_BODY%
) else (
    set OUTPUT=%THISNAME% %DC%%MSG_TITLE_F%%NN% %MSG_BODY%
)
call :_Print
endlocal
goto :eof

::: function PrintVersion(PRINT_LEVEL, MSG_TITLE, PV_APP, PV_VER, PV_ARCH, PV_PATCHES)
:PrintVersion
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_PrintVersion
:PCALL_PrintVersion
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_PrintVersion
set PRINT_LEVEL=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument PRINT_LEVEL" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintVersion" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set MSG_TITLE=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument MSG_TITLE" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintVersion" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set PV_APP=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument PV_APP" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintVersion" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set PV_VER=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument PV_VER" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintVersion" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set PV_ARCH=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument PV_ARCH" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintVersion" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift
set PV_PATCHES=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument PV_PATCHES" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintVersion" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift

:ArgCheckLoop_PrintVersion
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_PrintVersion
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintVersion" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_PrintVersion
:Main_PrintVersion
@set head=
@set next=
call :PreparePrint "%PRINT_LEVEL%" "%MSG_TITLE%"
call :ImportColor

:: request, match, newest
set OUTPUT=%THISNAME% %DP%%MSG_TITLE_F%%NN% %BW%%PV_APP%%NN%^=%PV_VER%%BW%%NN%@%PV_ARCH%[%PV_PATCHES%]
call :_Print
endlocal
goto :eof


:PrintTaskInfo::: function PrintTaskInfo()
:PrintTaskInfo
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_PrintTaskInfo
:PCALL_PrintTaskInfo
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_PrintTaskInfo

:ArgCheckLoop_PrintTaskInfo
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_PrintTaskInfo
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=print.cmd" & @set "ERROR_BLOCK=PrintTaskInfo" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_PrintTaskInfo
:Main_PrintTaskInfo
@set head=
@set next=
call :ImportColor

set PRINT_LEVEL=1
set MSG_TITLE=task
call :PreparePrint "%PRINT_LEVEL%" "%MSG_TITLE%"

set OUTPUT=%THISNAME% %BR%%MSG_TITLE_F%%NN% target:     %TARGETDIR%
call :_Print
set OUTPUT=                      name:       %NAME%
call :_Print
set OUTPUT=                      installer:  %INSTALLER%
call :_Print
endlocal
goto :eof



:_Print
if %PRINT_LEVEL% GEQ %LOG_LEVEL% echo.%OUTPUT%
goto :eof


:ImportColor
if not "%NN%" == "" goto :eof
if not "%NO_COLOR%" == "" goto :eof
if "%TEST_SHELL%" == "1" goto :eof

for /F "skip=1 delims=" %%F in ('
    wmic PATH Win32_LocalTime GET Day^,Month^,Year /FORMAT:TABLE
') do (
    for /F "tokens=1-3" %%L in ("%%F") do (
        set Day=0%%L
        set Month=0%%M
        set Year=%%N
    )
)
set Day=%Day:~-2%
set Month=%Month:~-2%

set ColorTable="%TEMP%\colortable%Year%%Month%%Day%.cmd"
if not exist "%ColorTable%" call :MakeColorTable "%ColorTable%"
call "%ColorTable%"

set Day=
set Month=
set Year=
set ColorTable=
goto :eof

::: function MakeColorTable(ColorTable) delayedexpansion
:MakeColorTable
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_MakeColorTable
:PCALL_MakeColorTable
@setlocal  enabledelayedexpansion
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_MakeColorTable
set ColorTable=%~1
if "%1" == "" @endlocal & ( @set "ERROR_MSG=Need argument ColorTable" & @set "ERROR_SOURCE=color.cmd" & @set "ERROR_BLOCK=MakeColorTable" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
shift

:ArgCheckLoop_MakeColorTable
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_MakeColorTable
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=color.cmd" & @set "ERROR_BLOCK=MakeColorTable" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_MakeColorTable
:Main_MakeColorTable
@set head=
@set next=
for /f %%a in ('"prompt $e & for %%b in (1) do rem"') do @set esc=%%a

set count=0
for %%A IN (K,R,G,Y,B,P,C,W) do call :SetAtomColor %%A

echo @set NN=%esc%[0m> "%ColorTable%"
for %%A IN (_FDK,_FDR,_FDG,_FDY,_FDB,_FDP,_FDC,_FDW, _FBK,_FBR,_FBG,_FBY,_FBB,_FBP,_FBC,_FBW) do (
    for %%B IN ("","") do call :SetColor %%A %%B
)

endlocal
goto :eof


:SetColor
@set Front=%~1
@set Back=%~2
@if "%Back%" == "" @(
    @echo @set %Front:~2%=%esc%[0;!%Front%!;40m>> "%ColorTable%"
) else @(
    @echo @set %Front:~1%%Back:~1%=%esc%[0;!%Front%!;!%Back%!m>> "%ColorTable%"
)
@goto :eof


:SetAtomColor
@set _FD%1=3%count%
@set _FB%1=1;3%count%
@set _BD%1=4%count%
@set _BB%1=4;4%count%
@set /A count+=1
@goto :eof




::: function CMD_update()
:CMD_update
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_CMD_update
:PCALL_CMD_update
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_CMD_update

:ArgCheckLoop_CMD_update
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_CMD_update
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=CMD_update.cmd" & @set "ERROR_BLOCK=CMD_update" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_CMD_update
:Main_CMD_update
@set head=
@set next=

if exist "%PRJ_CONF%\hooks\update.cmd" (
    call "%PRJ_CONF%\hooks\update.cmd"
)

endlocal
goto :eof

::: function CMD_clear()
:CMD_clear
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_CMD_clear
:PCALL_CMD_clear
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_CMD_clear

:ArgCheckLoop_CMD_clear
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_CMD_clear
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=CMD_clear.cmd" & @set "ERROR_BLOCK=CMD_clear" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_CMD_clear
:Main_CMD_clear
@set head=
@set next=



set inival=
call :GetIniArray DEVONE_CONFIG_PATH "clear"
(set Text=!inival!)&(set LoopCb=:clear_prject)&(set ExitCb=:exit_clear_prject)&(set Spliter=;)
goto :SubString
:clear_prject
    if exist "!PRJ_ROOT!\!substring!" call del "!PRJ_ROOT!\!substring!"
    goto :NextSubString
:exit_clear_prject
set inival=

if exist "%PRJ_CONF%\hooks\clear.cmd" (
    call "%PRJ_CONF%\hooks\clear.cmd"
)

endlocal
goto :eof

::: function CMD_exec()
:CMD_exec
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_CMD_exec
:PCALL_CMD_exec
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_CMD_exec

:ArgCheckLoop_CMD_exec
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_CMD_exec
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=CMD_exec" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_CMD_exec
:Main_CMD_exec
@set head=
@set next=

endlocal
goto :eof

::: function CMD_help()
:CMD_help
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
goto :NO_PCALL_CMD_help
:PCALL_CMD_help
@setlocal  
@echo off
set ERROR_MSG=
set ERROR_SOURCE=
set ERROR_BLOCK=
set ERROR_LINENO=
@set PCALL=1
:NO_PCALL_CMD_help

:ArgCheckLoop_CMD_help
set head=%~1
set next=%~2

if "%head%" == "" goto :GetRestArgs_CMD_help
if "%next%" == "" set next=__NONE__


 @endlocal & ( @set "ERROR_MSG=Unkwond option "%head%"" & @set "ERROR_SOURCE=dev-sh.cmd" & @set "ERROR_BLOCK=CMD_help" & @set "ERROR_LINENO=" & @if "%PCALL%" == "" @(@goto :_Error) else @(@goto :_ProtectError) )
:GetRestArgs_CMD_help
:Main_CMD_help
@set head=
@set next=

echo.  dev clear      for backup or clean re-install
echo.  dev update     update development environment
echo.  dev setup      configure git for first using
echo.  dev sync       keep project sync through git

endlocal
goto :eof











:_ProtectError
@goto :eof

:_Error
@echo ERROR: %ERROR_MSG%^

    at %ERROR_SOURCE%:%ERROR_BLOCK%:%ERROR_LINENO% 1>&2
@set ERROR_MSG=
@set ERROR_SOURCE=
@set ERROR_BLOCK=
@set ERROR_LINENO=
@exit /b 1


