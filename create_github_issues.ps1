# GitHub repository information
$owner = "nathaniel-auvil"
$repo = "pyworlds"

# Function to create an issue
function Create-GitHubIssue {
    param (
        [string]$Title,
        [string]$Body,
        [string]$Token
    )
    
    $headers = @{
        Authorization = "token $Token"
        Accept = "application/vnd.github.v3+json"
    }
    
    $body = @{
        title = $Title
        body = $Body
    } | ConvertTo-Json
    
    $url = "https://api.github.com/repos/$owner/$repo/issues"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -ContentType "application/json"
        Write-Host "Created issue: $Title"
        return $response
    }
    catch {
        Write-Host "Failed to create issue: $Title"
        Write-Host $_.Exception.Message
    }
}

# Prompt for GitHub token
$token = Read-Host "Enter your GitHub Personal Access Token"

# Epic 1: Core Systems Redesign
Create-GitHubIssue -Title "Implement core Mothership system" -Body @"
Convert existing planetary base to mothership system:
- [ ] Update GameState to center around mothership
- [ ] Implement basic mothership movement
- [ ] Add mothership health/shield systems
- [ ] Create basic resource storage system

Labels: enhancement, core-system
"@ -Token $token

Create-GitHubIssue -Title "Implement new resource system" -Body @"
Update resource types and collection mechanics:
- [ ] Add new resources (metal, gas, energy, refined materials)
- [ ] Implement resource collection from space
- [ ] Create resource refinement system
- [ ] Add resource storage limits per type

Labels: enhancement, resources
"@ -Token $token

# Add more issues here...
# (The rest of the issues from our list)

Write-Host "Finished creating issues!" 