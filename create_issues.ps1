$issues = @(
    @{
        title = "Implement core Mothership system"
        body = @"
Convert existing planetary base to mothership system:
- [ ] Update GameState to center around mothership
- [ ] Implement basic mothership movement
- [ ] Add mothership health/shield systems
- [ ] Create basic resource storage system

Labels: enhancement, core-system
"@
    },
    @{
        title = "Implement new resource system"
        body = @"
Update resource types and collection mechanics:
- [ ] Add new resources (metal, gas, energy, refined materials)
- [ ] Implement resource collection from space
- [ ] Create resource refinement system
- [ ] Add resource storage limits per type

Labels: enhancement, resources
"@
    },
    @{
        title = "Create ship module system"
        body = @"
Implement modular ship building system:
- [ ] Create base Module class
- [ ] Implement different module types (collectors, storage, production)
- [ ] Add module power requirements
- [ ] Add module crew requirements
- [ ] Implement module activation/deactivation

Labels: enhancement, modules
"@
    },
    @{
        title = "Implement fleet management system"
        body = @"
Create fleet management mechanics:
- [ ] Add support ships system
- [ ] Implement ship construction
- [ ] Create ship assignment system
- [ ] Add fleet movement controls

Labels: enhancement, fleet
"@
    },
    @{
        title = "Implement crew management system"
        body = @"
Create crew management features:
- [ ] Add crew hiring system
- [ ] Implement crew assignment to modules
- [ ] Add crew skills and experience
- [ ] Create crew training system

Labels: enhancement, crew
"@
    },
    @{
        title = "Implement space station trading"
        body = @"
Create trading mechanics:
- [ ] Dynamic pricing system
- [ ] Resource buy/sell interface
- [ ] Trade volume limits
- [ ] Price fluctuation based on supply/demand

Labels: enhancement, trading
"@
    },
    @{
        title = "Implement mission system"
        body = @"
Create mission mechanics:
- [ ] Add mission generation
- [ ] Create reward system
- [ ] Implement mission time limits
- [ ] Add mission difficulty progression

Labels: enhancement, missions
"@
    },
    @{
        title = "Implement blueprint system"
        body = @"
Create module blueprint mechanics:
- [ ] Add blueprint discovery
- [ ] Create blueprint research system
- [ ] Implement blueprint requirements
- [ ] Add blueprint trading

Labels: enhancement, blueprints
"@
    },
    @{
        title = "Implement space navigation system"
        body = @"
Create space movement mechanics:
- [ ] Add coordinate system
- [ ] Implement movement costs
- [ ] Create navigation interface
- [ ] Add speed/distance calculations

Labels: enhancement, navigation
"@
    },
    @{
        title = "Implement space resource locations"
        body = @"
Create resource collection points:
- [ ] Add resource fields
- [ ] Implement resource depletion
- [ ] Create resource regeneration
- [ ] Add resource quality variations

Labels: enhancement, resources
"@
    },
    @{
        title = "Implement space events system"
        body = @"
Create random event mechanics:
- [ ] Add space anomalies
- [ ] Implement space hazards
- [ ] Create emergency events
- [ ] Add event rewards/consequences

Labels: enhancement, events
"@
    }
)

# Get the repository owner and name from git remote
$remote = git remote get-url origin
$repoInfo = $remote -replace "https://github.com/", "" -replace ".git$", ""
$owner, $repo = $repoInfo.Split("/")

# Create each issue
foreach ($issue in $issues) {
    $body = @{
        title = $issue.title
        body = $issue.body
    } | ConvertTo-Json

    $headers = @{
        Authorization = "Bearer $env:GITHUB_TOKEN"
        Accept = "application/vnd.github.v3+json"
    }

    $url = "https://api.github.com/repos/$owner/$repo/issues"
    
    Write-Host "Creating issue: $($issue.title)"
    
    try {
        Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -ContentType "application/json"
        Write-Host "Successfully created issue: $($issue.title)"
        Start-Sleep -Seconds 1  # Add a small delay between requests
    }
    catch {
        Write-Host "Failed to create issue: $($issue.title)"
        Write-Host $_.Exception.Message
    }
} 