param(
    [string]$XlsxPath = "sample/moltbook_top1000_posts.xlsx",
    [string]$OutputRoot = "lakehouse"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-ExcelColumnName {
    param([int]$Index)

    $name = ""
    while ($Index -gt 0) {
        $mod = ($Index - 1) % 26
        $name = [char](65 + $mod) + $name
        $Index = [math]::Floor(($Index - 1) / 26)
    }
    return $name
}

function Get-CellValue {
    param(
        $Cell,
        [string[]]$SharedStrings
    )

    if (-not $Cell) {
        return $null
    }

    $raw = $null
    if ($Cell.PSObject.Properties.Name -contains "v") {
        $raw = $Cell.v
    } elseif ($Cell.PSObject.Properties.Name -contains "is") {
        $raw = $Cell.is.t
    }

    if ($null -eq $raw -or $raw -eq "") {
        return $null
    }

    $cellType = $null
    if ($Cell.PSObject.Properties.Name -contains "t") {
        $cellType = [string]$Cell.t
    }

    if ($cellType -eq "s") {
        return $SharedStrings[[int]$raw]
    }

    return $raw
}

$resolvedXlsx = (Resolve-Path $XlsxPath).Path
$resolvedOutputRoot = Join-Path (Resolve-Path ".").Path $OutputRoot

$bronzeDir = Join-Path $resolvedOutputRoot "bronze\moltbook"
$silverDir = Join-Path $resolvedOutputRoot "silver\moltbook"
$goldDir = Join-Path $resolvedOutputRoot "gold\moltbook"

New-Item -ItemType Directory -Force -Path $bronzeDir, $silverDir, $goldDir | Out-Null

$zip = [System.IO.Compression.ZipFile]::OpenRead($resolvedXlsx)
try {
    $sharedStringsEntry = $zip.GetEntry("xl/sharedStrings.xml")
    $sheetEntry = $zip.GetEntry("xl/worksheets/sheet1.xml")
    $tableEntry = $zip.GetEntry("xl/tables/table1.xml")

    $sharedStringsXml = [xml](New-Object System.IO.StreamReader($sharedStringsEntry.Open())).ReadToEnd()
    $sheetXml = [xml](New-Object System.IO.StreamReader($sheetEntry.Open())).ReadToEnd()
    $tableXml = [xml](New-Object System.IO.StreamReader($tableEntry.Open())).ReadToEnd()
}
finally {
    $zip.Dispose()
}

$sharedStrings = @()
foreach ($si in $sharedStringsXml.sst.si) {
    if ($si.t) {
        $sharedStrings += [string]$si.t
    } elseif ($si.r) {
        $sharedStrings += (($si.r | ForEach-Object { $_.t }) -join "")
    } else {
        $sharedStrings += ""
    }
}

$headers = @($tableXml.table.tableColumns.tableColumn | ForEach-Object { [string]$_.name })
$rows = New-Object System.Collections.Generic.List[object]

foreach ($row in $sheetXml.worksheet.sheetData.row) {
    if ([int]$row.r -eq 1) {
        continue
    }

    $record = [ordered]@{}
    for ($i = 0; $i -lt $headers.Count; $i++) {
        $record[$headers[$i]] = $null
    }

    foreach ($cell in $row.c) {
        $reference = [string]$cell.r
        $columnRef = ($reference -replace '\d', '')
        $headerIndex = [array]::IndexOf((1..$headers.Count | ForEach-Object { Get-ExcelColumnName $_ }), $columnRef)
        if ($headerIndex -ge 0) {
            $record[$headers[$headerIndex]] = Get-CellValue -Cell $cell -SharedStrings $sharedStrings
        }
    }

    $rows.Add([pscustomobject]$record)
}

$bronzeJsonlPath = Join-Path $bronzeDir "posts_top1000.jsonl"
$silverCsvPath = Join-Path $silverDir "posts_top1000.csv"
$goldCsvPath = Join-Path $goldDir "authors_summary.csv"

$rows | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 4 } | Set-Content $bronzeJsonlPath

$silverRows = foreach ($row in $rows) {
    [pscustomobject]@{
        rank_upvotes = [int]$row.rank_upvotes
        upvotes = [int]$row.upvotes
        downvotes = [int]$row.downvotes
        score = [int]$row.score
        comment_count = [int]$row.comment_count
        total_interactions = [int]$row.total_interactions
        comment_upvote_ratio = [double]$row.comment_upvote_ratio
        id = [string]$row.id
        post_url = [string]$row.post_url
        author = [string]$row.author
        submolt = [string]$row.submolt
        created_at = [string]$row.created_at
        title = [string]$row.title
        content = [string]$row.content
        title_len = [int]$row.title_len
        content_len = [int]$row.content_len
        first_link_url = [string]$row.first_link_url
        link_domain = [string]$row.link_domain
        extracted_at_utc = [string]$row.extracted_at_utc
        rank_score = [int]$row.rank_score
        rank_comments = [int]$row.rank_comments
        rank_total_interactions = [int]$row.rank_total_interactions
        net_votes = ([int]$row.upvotes - [int]$row.downvotes)
        engagement_count = ([int]$row.score + [int]$row.comment_count)
        title_chars = ([string]$row.title).Length
        content_chars = ([string]$row.content).Length
    }
}

$silverRows | Export-Csv -NoTypeInformation -Encoding UTF8 $silverCsvPath

$goldRows = $silverRows |
    Group-Object author |
    ForEach-Object {
        $items = $_.Group
        [pscustomobject]@{
            author = $_.Name
            post_count = $_.Count
            sum_upvotes = ($items | Measure-Object upvotes -Sum).Sum
            sum_comments = ($items | Measure-Object comment_count -Sum).Sum
            sum_interactions = ($items | Measure-Object total_interactions -Sum).Sum
            best_score = ($items | Measure-Object score -Maximum).Maximum
        }
    } |
    Sort-Object sum_interactions -Descending

$goldRows | Export-Csv -NoTypeInformation -Encoding UTF8 $goldCsvPath

$topAuthor = $goldRows | Select-Object -First 1

Write-Output "rows=$($rows.Count)"
Write-Output "columns=$($headers.Count)"
Write-Output "distinct_authors=$(($silverRows | Select-Object -ExpandProperty author | Sort-Object -Unique).Count)"
Write-Output "distinct_submolts=$(($silverRows | Select-Object -ExpandProperty submolt | Sort-Object -Unique).Count)"
Write-Output "top_author=$($topAuthor.author)"
Write-Output "top_author_sum_interactions=$($topAuthor.sum_interactions)"
Write-Output "bronze_jsonl=$bronzeJsonlPath"
Write-Output "silver_csv=$silverCsvPath"
Write-Output "gold_csv=$goldCsvPath"
