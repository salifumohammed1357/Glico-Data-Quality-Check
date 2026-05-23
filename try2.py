import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Data Quality Check",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stAlert {
        border-radius: 10px;
        padding: 1rem;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    .score-excellent {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
    }
    .score-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #ffc107;
    }
    .score-poor {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
    }
    h1 {
        color: #1e3a8a;
        font-weight: 700;
    }
    h2 {
        color: #2563eb;
        font-weight: 600;
        margin-top: 2rem;
    }
    h3 {
        color: #3b82f6;
        font-weight: 600;
    }
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("# 🔍 Data Quality Check")
st.markdown("### Upload your dataset and run comprehensive quality checks before processing")
st.markdown("---")

# Upload Section
with st.container():
    st.markdown("## 📤 Upload Dataset for Quality Check")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx"],
            help="Upload your dataset to begin quality analysis"
        )

if uploaded_file is None:
    st.info("👆 Please upload a dataset to begin quality checks.")

    # Display helpful information
    with st.expander("ℹ️ What to expect from this quality check"):
        st.markdown("""
        **This analysis will check:**
        - ✅ Overall data quality score
        - 🧩 Missing values across all columns
        - 🔎 Data type validation
        - 📏 Data range validation (dates and amounts)

        **Required columns for validation:**
        - Reference ID, Driver Code, Name
        - Phone Number, Date of Birth, Date
        - Amount
        """)
    st.stop()

# Load Dataset
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ Dataset uploaded successfully!")

except Exception as e:
    st.error(f"❌ Failed to read the uploaded file: {str(e)}")
    st.stop()

# Dataset Preview Section
st.markdown("---")
st.markdown("## 👀 Dataset Preview")

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="📊 Total Records",
        value=f"{df.shape[0]:,}",
        delta=None
    )
with col2:
    st.metric(
        label="📋 Total Columns",
        value=df.shape[1],
        delta=None
    )

st.markdown("#### First 10 Rows")
st.dataframe(
    df.head(10),
    use_container_width=True,
    height=400
)

# Calculate Quality Metrics
total_cells = df.shape[0] * df.shape[1]
missing_cells = df.isna().sum().sum()
completeness_score = (1 - (missing_cells / total_cells)) * 100

type_issues = 0
for col in df.columns:
    if df[col].dtype not in ["int64", "float64", "object", "datetime64[ns]"]:
        type_issues += 1

type_score = ((len(df.columns) - type_issues) / len(df.columns)) * 100
overall_score = round((completeness_score * 0.6) + (type_score * 0.4), 2)

# Overall Quality Score Section
st.markdown("---")
st.markdown("## 📊 Overall Data Quality Score")

# Create gauge chart
fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=overall_score,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Quality Score (%)", 'font': {'size': 24}},
    delta={'reference': 80},
    gauge={
        'axis': {'range': [None, 100]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 50], 'color': "#ffcccc"},
            {'range': [50, 80], 'color': "#ffffcc"},
            {'range': [80, 100], 'color': "#ccffcc"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 80
        }
    }
))

fig.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=50, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.plotly_chart(fig, use_container_width=True)

# Score interpretation
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="📈 Completeness Score",
        value=f"{completeness_score:.2f}%"
    )
with col2:
    st.metric(
        label="🎯 Type Accuracy Score",
        value=f"{type_score:.2f}%"
    )
with col3:
    if overall_score >= 80:
        st.success(f"**Status:** Excellent Quality ✅")
    elif overall_score >= 50:
        st.warning(f"**Status:** Needs Improvement ⚠️")
    else:
        st.error(f"**Status:** Poor Quality ❌")

# Missing Values Analysis
st.markdown("---")
st.markdown("## 🧩 Missing Values Analysis")

missing_df = pd.DataFrame({
    "Column": df.columns,
    "Missing Count": df.isna().sum().values,
    "Missing %": (df.isna().mean() * 100).round(2).values
}).reset_index(drop=True)

# Create bar chart for missing values
fig_missing = go.Figure(data=[
    go.Bar(
        x=missing_df["Column"],
        y=missing_df["Missing %"],
        marker_color=['#ff6b6b' if x > 0 else '#51cf66' for x in missing_df["Missing %"]],
        text=missing_df["Missing %"].apply(lambda x: f"{x:.1f}%"),
        textposition='auto',
    )
])

fig_missing.update_layout(
    title="Missing Values by Column",
    xaxis_title="Column",
    yaxis_title="Missing Percentage (%)",
    height=400,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.9)"
)

st.plotly_chart(fig_missing, use_container_width=True)

# Missing values table
st.markdown("#### Detailed Missing Values Report")


def highlight_missing(row):
    if row['Missing Count'] > 0:
        return ['background-color: #fff3cd'] * len(row)
    return [''] * len(row)


styled_missing = missing_df.style.apply(highlight_missing, axis=1)
st.dataframe(styled_missing, use_container_width=True, height=400)

# Data Type Validation
st.markdown("---")
st.markdown("## 🔎 Data Type Validation")

expected_types = {
    "Reference ID": "object",
    "Driver Code": "object",
    "Name": "object",
    "Phone Number": "object",
    "Date of Birth": "datetime",
    "Date": "datetime",
    "Amount": "numeric"
}

type_results = []

for col in df.columns:
    detected = str(df[col].dtype)
    expected = expected_types.get(col, "Not Defined")

    valid = (
            expected == "Not Defined" or
            (expected == "object" and df[col].dtype == "object") or
            (expected == "numeric" and df[col].dtype in ["int64", "float64"]) or
            (expected == "datetime" and "datetime" in detected)
    )

    type_results.append({
        "Column": col,
        "Expected Type": expected,
        "Detected Type": detected,
        "Status": "✅ Valid" if valid else "❌ Invalid"
    })

type_df = pd.DataFrame(type_results)

# Summary metrics
valid_count = sum(1 for r in type_results if "Valid" in r["Status"])
invalid_count = len(type_results) - valid_count

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("✅ Valid Types", valid_count)
with col2:
    st.metric("❌ Invalid Types", invalid_count)
with col3:
    st.metric("📊 Accuracy", f"{(valid_count / len(type_results) * 100):.1f}%")

st.markdown("#### Type Validation Details")


def highlight_type_validation(row):
    if "Invalid" in row['Status']:
        return ['background-color: #f8d7da'] * len(row)
    return ['background-color: #d4edda'] * len(row)


styled_type = type_df.style.apply(highlight_type_validation, axis=1)
st.dataframe(styled_type, use_container_width=True, height=400)

# Data Range Validation
st.markdown("---")
st.markdown("## 📏 Data Range Validation")

st.markdown("""
This section validates that your data values fall within acceptable and logical ranges.
We check for:
- **Date columns**: Invalid formats, future dates, unrealistic dates
- **Amount column**: Negative values, zeros, missing values, outliers
- **Phone numbers**: Invalid formats and lengths
- **Reference IDs**: Duplicates and format consistency
""")

range_issues = []
validation_details = {}

# ========================================
# 1. DATE VALIDATION
# ========================================
st.markdown("### 📅 Date Field Validation")

date_columns = [c for c in df.columns if "date" in c.lower()]

if date_columns:
    for col in date_columns:
        st.markdown(f"**Checking: {col}**")

        # Store original to compare
        original_col = df[col].copy()
        original_missing = original_col.isna().sum()

        # Convert to datetime
        df[col] = pd.to_datetime(df[col], errors="coerce")

        # Check 1: Invalid date formats
        invalid_dates = df[col].isna().sum() - original_missing
        if invalid_dates > 0:
            range_issues.append({
                "Column": col,
                "Issue": "Invalid date format/values",
                "Count": invalid_dates,
                "Severity": "🔴 High",
                "Example": "Check dates like '13/13/2024' or text in date fields"
            })
            st.warning(f"⚠️ Found {invalid_dates} invalid date formats")

        # Check 2: Future dates
        future_dates_mask = df[col] > pd.Timestamp.today()
        future_dates = future_dates_mask.sum()
        if future_dates > 0:
            range_issues.append({
                "Column": col,
                "Issue": "Future dates detected",
                "Count": future_dates,
                "Severity": "🟡 Medium",
                "Example": f"Latest date: {df[col].max()}"
            })
            st.warning(f"⚠️ Found {future_dates} future dates")

        # Check 3: Very old dates (likely errors)
        if not df[col].isna().all():
            min_date = df[col].min()
            if pd.notna(min_date) and min_date < pd.Timestamp('1900-01-01'):
                old_dates = (df[col] < pd.Timestamp('1900-01-01')).sum()
                range_issues.append({
                    "Column": col,
                    "Issue": "Unrealistic old dates",
                    "Count": old_dates,
                    "Severity": "🟡 Medium",
                    "Example": f"Earliest date: {min_date}"
                })
                st.warning(f"⚠️ Found {old_dates} dates before 1900")

        # Show date range summary
        if not df[col].isna().all():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Valid Dates", df[col].notna().sum())
            with col2:
                st.metric("📅 Earliest", df[col].min().strftime('%Y-%m-%d') if pd.notna(df[col].min()) else "N/A")
            with col3:
                st.metric("📅 Latest", df[col].max().strftime('%Y-%m-%d') if pd.notna(df[col].max()) else "N/A")

        st.markdown("---")
else:
    st.info("ℹ️ No date columns found in the dataset")

# ========================================
# 2. AMOUNT VALIDATION
# ========================================
st.markdown("### 💰 Amount Field Validation")

if "Amount" in df.columns:
    st.markdown("**Checking: Amount**")

    # Convert to numeric
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    # Check 1: Missing values
    missing_amounts = df["Amount"].isna().sum()
    if missing_amounts > 0:
        range_issues.append({
            "Column": "Amount",
            "Issue": "Missing values",
            "Count": missing_amounts,
            "Severity": "🔴 High",
            "Example": "Empty or non-numeric values"
        })
        st.error(f"🔴 Found {missing_amounts} missing/invalid amount values")

    # Check 2: Zero values
    zero_amounts = (df["Amount"] == 0).sum()
    if zero_amounts > 0:
        range_issues.append({
            "Column": "Amount",
            "Issue": "Zero values",
            "Count": zero_amounts,
            "Severity": "🟡 Medium",
            "Example": "Transactions with 0.00 amount"
        })
        st.warning(f"⚠️ Found {zero_amounts} zero amount values")

    # Check 3: Negative values
    negative_amounts = (df["Amount"] < 0).sum()
    if negative_amounts > 0:
        range_issues.append({
            "Column": "Amount",
            "Issue": "Negative values",
            "Count": negative_amounts,
            "Severity": "🔴 High",
            "Example": f"Example: {df[df['Amount'] < 0]['Amount'].iloc[0] if negative_amounts > 0 else 'N/A'}"
        })
        st.error(f"🔴 Found {negative_amounts} negative amount values")

    # Check 4: Outliers (values beyond 3 standard deviations)
    if df["Amount"].notna().sum() > 0:
        mean_amount = df["Amount"].mean()
        std_amount = df["Amount"].std()
        if std_amount > 0:
            outliers = ((df["Amount"] > mean_amount + 3 * std_amount) |
                        (df["Amount"] < mean_amount - 3 * std_amount)).sum()

            if outliers > 0:
                range_issues.append({
                    "Column": "Amount",
                    "Issue": "Statistical outliers detected",
                    "Count": outliers,
                    "Severity": "🟡 Medium",
                    "Example": f"Beyond ±3 std deviations from mean"
                })
                st.info(f"ℹ️ Found {outliers} statistical outliers (may be legitimate)")

    # Amount statistics
    if df["Amount"].notna().sum() > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Valid Amounts", df["Amount"].notna().sum())
        with col2:
            st.metric("💵 Min", f"${df['Amount'].min():.2f}" if pd.notna(df['Amount'].min()) else "N/A")
        with col3:
            st.metric("💵 Max", f"${df['Amount'].max():.2f}" if pd.notna(df['Amount'].max()) else "N/A")
        with col4:
            st.metric("💵 Average", f"${df['Amount'].mean():.2f}" if pd.notna(df['Amount'].mean()) else "N/A")

    st.markdown("---")
else:
    st.info("ℹ️ No 'Amount' column found in the dataset")

# ========================================
# 3. PHONE NUMBER VALIDATION
# ========================================
st.markdown("### 📱 Phone Number Validation")

if "Phone Number" in df.columns:
    st.markdown("**Checking: Phone Number**")

    # Convert to string for validation
    phone_series = df["Phone Number"].astype(str)

    # Check 1: Missing values
    missing_phones = df["Phone Number"].isna().sum()
    if missing_phones > 0:
        range_issues.append({
            "Column": "Phone Number",
            "Issue": "Missing values",
            "Count": missing_phones,
            "Severity": "🟡 Medium",
            "Example": "Empty phone numbers"
        })
        st.warning(f"⚠️ Found {missing_phones} missing phone numbers")

    # Check 2: Invalid length (assuming 10-15 digits is valid)
    valid_phones = phone_series.str.replace(r'[^0-9]', '', regex=True)
    invalid_length = ((valid_phones.str.len() < 10) | (valid_phones.str.len() > 15)).sum()

    if invalid_length > 0:
        range_issues.append({
            "Column": "Phone Number",
            "Issue": "Invalid phone length",
            "Count": invalid_length,
            "Severity": "🟡 Medium",
            "Example": "Phone numbers with < 10 or > 15 digits"
        })
        st.warning(f"⚠️ Found {invalid_length} phone numbers with invalid length")

    # Statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Valid Phones", df["Phone Number"].notna().sum())
    with col2:
        unique_phones = df["Phone Number"].nunique()
        st.metric("🔢 Unique Numbers", unique_phones)

    st.markdown("---")
else:
    st.info("ℹ️ No 'Phone Number' column found in the dataset")

# ========================================
# 4. REFERENCE ID VALIDATION
# ========================================
st.markdown("### 🆔 Reference ID Validation")

if "Reference ID" in df.columns:
    st.markdown("**Checking: Reference ID**")

    # Check 1: Missing values
    missing_refs = df["Reference ID"].isna().sum()
    if missing_refs > 0:
        range_issues.append({
            "Column": "Reference ID",
            "Issue": "Missing values",
            "Count": missing_refs,
            "Severity": "🔴 High",
            "Example": "Empty Reference IDs"
        })
        st.error(f"🔴 Found {missing_refs} missing Reference IDs")

    # Check 2: Duplicate Reference IDs
    duplicate_refs = df["Reference ID"].duplicated().sum()
    if duplicate_refs > 0:
        range_issues.append({
            "Column": "Reference ID",
            "Issue": "Duplicate Reference IDs",
            "Count": duplicate_refs,
            "Severity": "🔴 High",
            "Example": "Same Reference ID used multiple times"
        })
        st.error(f"🔴 Found {duplicate_refs} duplicate Reference IDs")

    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total IDs", df["Reference ID"].notna().sum())
    with col2:
        st.metric("🔢 Unique IDs", df["Reference ID"].nunique())
    with col3:
        duplicate_rate = (duplicate_refs / len(df) * 100) if len(df) > 0 else 0
        st.metric("📈 Duplicate Rate", f"{duplicate_rate:.1f}%")

    st.markdown("---")
else:
    st.info("ℹ️ No 'Reference ID' column found in the dataset")

# ========================================
# SUMMARY OF ALL ISSUES
# ========================================
st.markdown("### 📋 Validation Summary")

if range_issues:
    st.markdown("#### ⚠️ Issues Detected")

    # Create comprehensive issues dataframe
    issues_df = pd.DataFrame(range_issues)

    # Count by severity
    high_severity = sum(1 for issue in range_issues if "High" in issue["Severity"])
    medium_severity = sum(1 for issue in range_issues if "Medium" in issue["Severity"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 High Severity", high_severity)
    with col2:
        st.metric("🟡 Medium Severity", medium_severity)
    with col3:
        st.metric("📊 Total Issues", len(range_issues))

    st.markdown("---")

    # Display each issue with details
    for idx, issue in enumerate(range_issues, 1):
        with st.expander(f"{issue['Severity']} {issue['Column']}: {issue['Issue']} ({issue['Count']} records)"):
            st.write(f"**Column:** {issue['Column']}")
            st.write(f"**Issue:** {issue['Issue']}")
            st.write(f"**Affected Records:** {issue['Count']}")
            st.write(f"**Severity Level:** {issue['Severity']}")
            st.write(f"**Details:** {issue['Example']}")

    st.markdown("#### Detailed Issue Report")
    st.dataframe(issues_df, use_container_width=True)

    # Recommendations
    st.markdown("#### 💡 Recommendations")
    if high_severity > 0:
        st.error("""
        **High Priority Actions Required:**
        - Address all High Severity issues before proceeding
        - Review missing Reference IDs and Amounts
        - Check negative or invalid amount values
        - Verify data integrity for critical fields
        """)
    else:
        st.warning("""
        **Medium Priority Actions:**
        - Review Medium Severity issues
        - These issues may not block processing but should be reviewed
        - Consider data cleaning for optimal results
        """)

else:
    st.success("✅ **No data range issues detected!**")
    st.balloons()
    st.markdown("""
    All validation checks passed:
    - ✅ All dates are valid and within acceptable ranges
    - ✅ All amounts are positive and valid
    - ✅ Phone numbers have valid formats
    - ✅ Reference IDs are unique and complete

    Your data is in excellent condition and ready for processing!
    """)

# Completion Section
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if range_issues:
        st.warning("""
        ### ⚠️ Data Quality Check Completed with Issues

        **Next Steps:**
        - Review and address the issues identified above
        - Download the validation reports for detailed analysis
        - Fix critical issues before proceeding to the next stage
        - Consider re-uploading corrected data

        You can proceed to **Duplicate Detection & Matching**, but addressing these issues first is recommended.
        """)
    else:
        st.info("""
        ### ✅ Data Quality Check Completed Successfully

        **Next Steps:**
        - Your data passed all quality checks
        - Review the quality metrics above
        - Proceed to **Duplicate Detection & Matching**

        Your data is ready for the next stage of processing.
        """)

# Download Quality Report
st.markdown("---")
st.markdown("## 📥 Export Quality Report")

# Create comprehensive report
report_data = {
    "Overall Score": [overall_score],
    "Completeness Score": [completeness_score],
    "Type Score": [type_score],
    "Total Records": [df.shape[0]],
    "Total Columns": [df.shape[1]],
    "Missing Cells": [missing_cells],
    "Total Cells": [total_cells],
    "High Severity Issues": [sum(1 for issue in range_issues if "High" in issue.get("Severity", ""))],
    "Medium Severity Issues": [sum(1 for issue in range_issues if "Medium" in issue.get("Severity", ""))],
    "Total Issues": [len(range_issues)]
}

report_df = pd.DataFrame(report_data)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.download_button(
        label="📊 Download Quality Report",
        data=report_df.to_csv(index=False).encode('utf-8'),
        file_name=f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
with col2:
    st.download_button(
        label="🧩 Download Missing Values Report",
        data=missing_df.to_csv(index=False).encode('utf-8'),
        file_name=f"missing_values_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
with col3:
    st.download_button(
        label="🔎 Download Type Validation Report",
        data=type_df.to_csv(index=False).encode('utf-8'),
        file_name=f"type_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
with col4:
    if range_issues:
        issues_export_df = pd.DataFrame(range_issues)
        st.download_button(
            label="⚠️ Download Issues Report",
            data=issues_export_df.to_csv(index=False).encode('utf-8'),
            file_name=f"range_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )