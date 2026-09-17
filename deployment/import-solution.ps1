param(
    [Parameter(Mandatory=$true)][string]$EnvironmentUrl,
    [Parameter(Mandatory=$true)][string]$SolutionZip,
    [string]$SettingsFile = "./deployment/deployment-settings.json"
)

$ErrorActionPreference = "Stop"
pac auth create --environment $EnvironmentUrl
if (Test-Path $SettingsFile) {
    pac solution import --path $SolutionZip --settings-file $SettingsFile --publish-changes
} else {
    pac solution import --path $SolutionZip --publish-changes
}
