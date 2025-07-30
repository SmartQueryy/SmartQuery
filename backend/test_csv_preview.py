#!/usr/bin/env python3
"""
Test script for CSV preview endpoint - Task B18
"""

import io
import pandas as pd
from unittest.mock import Mock, patch
from api.chat import _load_csv_preview_from_storage, _generate_preview_from_metadata

def test_load_csv_preview_from_storage():
    """Test loading CSV preview from storage"""
    
    # Create sample CSV data
    sample_csv = """name,age,city,salary
Alice,25,New York,75000
Bob,30,Los Angeles,85000
Charlie,35,Chicago,90000
Diana,28,Houston,80000
Eve,32,Phoenix,77000"""
    
    # Mock project object
    mock_project = Mock()
    mock_project.csv_path = "test/sample.csv"
    
    # Mock storage service
    with patch('api.chat.storage_service') as mock_storage:
        mock_storage.download_file.return_value = sample_csv.encode('utf-8')
        
        # Test the function
        result = _load_csv_preview_from_storage(mock_project)
        
        # Verify results
        assert result is not None
        assert result.columns == ["name", "age", "city", "salary"]
        assert len(result.sample_data) == 5  # Should have 5 rows
        assert result.total_rows == 5
        assert result.data_types["name"] == "string"
        assert result.data_types["age"] == "number"
        assert result.data_types["salary"] == "number"
        
        # Check sample data
        assert result.sample_data[0] == ["Alice", 25, "New York", 75000]
        assert result.sample_data[1] == ["Bob", 30, "Los Angeles", 85000]
        
        print("✅ CSV preview from storage test passed!")

def test_generate_preview_from_metadata():
    """Test generating preview from metadata"""
    
    # Mock project object with metadata
    mock_project = Mock()
    mock_project.row_count = 100
    mock_project.columns_metadata = [
        {
            "name": "product_name",
            "type": "string",
            "sample_values": ["Product A", "Product B", "Product C"]
        },
        {
            "name": "sales_amount", 
            "type": "number",
            "sample_values": [1500.0, 2300.5, 1890.25]
        },
        {
            "name": "date",
            "type": "date",
            "sample_values": ["2024-01-01", "2024-01-02", "2024-01-03"]
        }
    ]
    
    # Test the function
    result = _generate_preview_from_metadata(mock_project)
    
    # Verify results
    assert result is not None
    assert result.columns == ["product_name", "sales_amount", "date"]
    assert len(result.sample_data) == 5  # Should have 5 rows
    assert result.total_rows == 100
    assert result.data_types["product_name"] == "string"
    assert result.data_types["sales_amount"] == "number"
    assert result.data_types["date"] == "date"
    
    # Check sample data uses actual sample values
    assert result.sample_data[0] == ["Product A", 1500.0, "2024-01-01"]
    assert result.sample_data[1] == ["Product B", 2300.5, "2024-01-02"]
    assert result.sample_data[2] == ["Product C", 1890.25, "2024-01-03"]
    
    print("✅ CSV preview from metadata test passed!")

def test_csv_data_types_detection():
    """Test data type detection for different CSV column types"""
    
    # Create CSV with various data types
    sample_csv = """id,name,active,price,created_date,rating
1,Product A,true,19.99,2024-01-01,4.5
2,Product B,false,29.99,2024-01-02,3.8
3,Product C,true,39.99,2024-01-03,4.2"""
    
    mock_project = Mock()
    mock_project.csv_path = "test/types.csv"
    
    with patch('api.chat.storage_service') as mock_storage:
        mock_storage.download_file.return_value = sample_csv.encode('utf-8')
        
        result = _load_csv_preview_from_storage(mock_project)
        
        assert result is not None
        assert result.data_types["id"] == "number"
        assert result.data_types["name"] == "string"
        assert result.data_types["active"] == "boolean"
        assert result.data_types["price"] == "number"
        assert result.data_types["rating"] == "number"
        
        print("✅ Data type detection test passed!")

if __name__ == "__main__":
    print("Testing CSV Preview Endpoint - Task B18")
    print("=" * 50)
    
    test_load_csv_preview_from_storage()
    test_generate_preview_from_metadata() 
    test_csv_data_types_detection()
    
    print("\n🎉 All CSV preview tests passed!")
    print("Task B18 implementation verified!")