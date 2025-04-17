from getApexLog import salesforce_login, getApexLogs, downloadApexLog
from unittest.mock import patch, MagicMock


@patch("getApexLog.Salesforce")
def test_salesforce_login(mock_salesforce):
    # Mock Salesforce instance
    mock_instance = MagicMock()
    mock_salesforce.return_value = mock_instance

    # Test valid credentials
    creds = ["test_instance", "test_token"]
    sf = salesforce_login(creds)
    assert sf == mock_instance
    mock_salesforce.assert_called_once_with(
        instance="test_instance", session_id="test_token", version="62.0"
    )

    # Test invalid credentials
    mock_salesforce.side_effect = Exception("Login failed")
    sf = salesforce_login(creds)
    assert sf is None


@patch("getApexLog.format_soql")
def test_getApexLogs(mock_format_soql):

    # Mock SOQL formatting
    mock_format_soql.return_value = """
        SELECT Id, StartTime, Location, LogLength
        FROM ApexLog
        WHERE LogLength > 500
        AND StartTime = TODAY
        ORDER BY LogLength DESC
    """

    # Mock Salesforce query result
    row0 = {
        "attributes": {
            "type": "ApexLog",
            "url": "/services/data/v62.0/sobjects/ApexLog/07LUE000009slSz2AI",
        },
        "Id": "07LUE000009slSz2AI",
        "StartTime": "2025-04-17T09:43:13.000+0000",
        "Location": "SystemLog",
        "LogLength": 13864,
    }

    row1 = {
        "attributes": {
            "type": "ApexLog",
            "url": "/services/data/v62.0/sobjects/ApexLog/07LUE000009shu62AA",
        },
        "Id": "07LUE000009shu62AA",
        "StartTime": "2025-04-17T09:43:13.000+0000",
        "Location": "SystemLog",
        "LogLength": 13861,
    }

    row2 = {
        "attributes": {
            "type": "ApexLog",
            "url": "/services/data/v62.0/sobjects/ApexLog/07LUE000009sdhB2AQ",
        },
        "Id": "07LUE000009sdhB2AQ",
        "StartTime": "2025-04-17T09:43:13.000+0000",
        "Location": "SystemLog",
        "LogLength": 13860,
    }

    # Mock Salesforce instance
    sf = MagicMock()
    sf.query.return_value = {"records": [row0, row1, row2]}

    # Call the function
    df = getApexLogs(sf, 500)

    # Assertions
    assert not df.empty
    assert len(df) == 3  # Should match the number of mocked rows
    assert "Id" in df.columns
    assert "StartTime" in df.columns
    assert "Location" in df.columns
    assert "LogLength" in df.columns

    # Verify mocks
    mock_format_soql.assert_called_once()
    sf.query.assert_called_once_with(mock_format_soql.return_value)


@patch("getApexLog.requests.get")
def test_downloadApexLog(mock_get):
    # Mock request response
    mock_response = MagicMock()
    mock_response.content = b"Test log content"
    mock_get.return_value = mock_response

    # Test function
    sf = MagicMock()
    sf.sf_instance = "test_instance"
    sf.headers = {"Authorization": "Bearer test_token"}
    log_content = downloadApexLog(sf, "test_log_id")
    assert log_content == b"Test log content"
    mock_get.assert_called_once_with(
        "https://test_instance/apexdebug/traceDownload.apexp?id=test_log_id",
        headers={"Authorization": "Bearer test_token"},
    )
