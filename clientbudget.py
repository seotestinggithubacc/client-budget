import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# Page configuration
st.set_page_config(
    page_title="Marketing Budget Calculator",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for depth design with your color palette
st.markdown("""
<style>
:root {
    --primary-1: #880808;
    --primary-2: #3B429F;
    --primary-3: #AA7DCE;
    --secondary-1: #F5D7E3;
    --secondary-2: #A6E1FA;
    --bg-light: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #1a1a1a;
    --text-secondary: #6c757d;
    
    /* Shadow variables for depth */
    --shadow-s: 0 2px 8px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
    --shadow-m: 0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.1);
    --shadow-l: 0 8px 32px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.12);
    --shadow-inset: inset 0 1px 3px rgba(0,0,0,0.1), inset 0 -1px 3px rgba(0,0,0,0.05);
}

.stApp {
    background: linear-gradient(135deg, var(--secondary-2) 0%, var(--secondary-1) 100%);
    font-family: 'Segoe UI', system-ui, sans-serif;
}

/* Main container styling */
.main-header {
    background: var(--bg-light);
    border-radius: 16px;
    box-shadow: var(--shadow-m);
    padding: 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(255,255,255,0.8);
}

/* Card containers */
.card {
    background: var(--bg-light);
    border-radius: 12px;
    box-shadow: var(--shadow-s);
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.9);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: var(--shadow-m);
    transform: translateY(-2px);
}

/* Sidebar styling */
.css-1d391kg {
    background: var(--bg-light);
    border-radius: 0 16px 16px 0;
    box-shadow: var(--shadow-l);
    border-right: 1px solid rgba(255,255,255,0.8);
}

/* Button styling with depth */
.stButton > button {
    border-radius: 8px;
    box-shadow: var(--shadow-s);
    border: none;
    background: linear-gradient(135deg, var(--primary-1) 0%, var(--primary-2) 100%);
    color: white;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    box-shadow: var(--shadow-m);
    transform: translateY(-1px);
    background: linear-gradient(135deg, var(--primary-2) 0%, var(--primary-3) 100%);
}

.stButton > button:active {
    box-shadow: var(--shadow-inset);
    transform: translateY(0);
}

/* Input fields with depth */
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stMultiselect > div > div > div {
    border-radius: 8px;
    box-shadow: var(--shadow-inset);
    border: 1px solid #e9ecef;
    background: var(--bg-light);
    transition: all 0.3s ease;
}

.stNumberInput > div > div > input:focus,
.stSelectbox > div > div > div:focus,
.stMultiselect > div > div > div:focus {
    box-shadow: 0 0 0 2px var(--primary-3), var(--shadow-inset);
    border-color: var(--primary-3);
}

/* Dataframe styling */
.dataframe {
    border-radius: 8px;
    box-shadow: var(--shadow-s);
    border: 1px solid rgba(255,255,255,0.8);
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--bg-light);
    border-radius: 12px;
    box-shadow: var(--shadow-s);
    padding: 1rem;
    border: 1px solid rgba(255,255,255,0.8);
}

/* Success/Info boxes */
.stSuccess, .stInfo {
    border-radius: 8px;
    box-shadow: var(--shadow-s);
    border: 1px solid rgba(255,255,255,0.8);
}

/* Download button specific styling */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--primary-3) 0%, #8a4fff 100%);
    border-radius: 8px;
    box-shadow: var(--shadow-s);
    border: none;
    color: white;
    transition: all 0.3s ease;
}

.stDownloadButton > button:hover {
    box-shadow: var(--shadow-m);
    transform: translateY(-1px);
}

/* Progress bar styling */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--primary-1), var(--primary-3));
    border-radius: 4px;
    box-shadow: var(--shadow-inset);
}

/* Custom header styling */
.custom-header {
    background: linear-gradient(135deg, var(--primary-1), var(--primary-2));
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: var(--shadow-m);
    margin-bottom: 1.5rem;
}

/* Results table styling */
.results-table {
    background: var(--bg-light);
    border-radius: 12px;
    box-shadow: var(--shadow-m);
    padding: 1.5rem;
    border: 1px solid rgba(255,255,255,0.8);
}

/* Stats container */
.stats-container {
    background: linear-gradient(135deg, var(--secondary-1), var(--secondary-2));
    border-radius: 12px;
    box-shadow: var(--shadow-s);
    padding: 1.5rem;
    border: 1px solid rgba(255,255,255,0.8);
}

/* Hover effects for interactive elements */
.interactive-card {
    cursor: pointer;
    transition: all 0.3s ease;
}

.interactive-card:hover {
    box-shadow: var(--shadow-l);
    transform: translateY(-3px);
}

/* Custom checkbox styling */
.stCheckbox > label {
    border-radius: 6px;
    padding: 0.5rem;
    transition: all 0.3s ease;
}

.stCheckbox > label:hover {
    background: var(--secondary-1);
    box-shadow: var(--shadow-s);
}
</style>
""", unsafe_allow_html=True)

class MarketingBudgetCalculator:
    def __init__(self):
        self.channels = {
            'SEO': 'Search Engine Optimization',
            'PAID_SEARCH': 'Paid Search (Google Ads, etc.)',
            'PAID_SOCIAL': 'Paid Social Media',
            'CONTENT_MARKETING': 'Content Marketing',
            'EMAIL_MARKETING': 'Email Marketing',
            'INFLUENCER': 'Influencer Marketing',
            'PR': 'Public Relations',
            'EVENTS': 'Events & Webinars',
            'AFFILIATE': 'Affiliate Marketing',
            'LLM_OPTIMIZATION': 'LLM Visibility Optimization'
        }
        
        self.goals = {
            'LOW_COST_ACQUISITION': 'Acquire at lowest cost (time not critical)',
            'PRODUCT_VALIDATION': 'Validate product USP/messaging',
            'BRAND_AWARENESS': 'Build brand awareness',
            'LLM_VISIBILITY': 'Maximize LLM visibility',
            'RAPID_GROWTH': 'Rapid customer acquisition',
            'LEAD_GENERATION': 'Generate qualified leads'
        }

    def calculate_allocation(self, total_budget, primary_goal, secondary_goals=None, industry_data=None):
        if secondary_goals is None:
            secondary_goals = []
        
        # Use industry data if available, otherwise use default
        if industry_data:
            base_allocation = industry_data
        else:
            base_allocation = self._get_default_allocation(total_budget)
        
        adjusted_allocation = self._apply_goal_adjustments(
            base_allocation, primary_goal, secondary_goals
        )
        
        final_allocation = self._normalize_allocation(adjusted_allocation, total_budget)
        return final_allocation

    def _get_default_allocation(self, budget):
        # Default allocation based on budget size
        if budget < 10000:
            return {
                'SEO': 35, 'PAID_SEARCH': 10, 'PAID_SOCIAL': 5, 'CONTENT_MARKETING': 25,
                'EMAIL_MARKETING': 15, 'INFLUENCER': 0, 'PR': 5, 'EVENTS': 0, 'AFFILIATE': 0,
                'LLM_OPTIMIZATION': 5
            }
        elif budget < 50000:
            return {
                'SEO': 20, 'PAID_SEARCH': 20, 'PAID_SOCIAL': 15, 'CONTENT_MARKETING': 15,
                'EMAIL_MARKETING': 10, 'INFLUENCER': 5, 'PR': 5, 'EVENTS': 5, 'AFFILIATE': 3,
                'LLM_OPTIMIZATION': 2
            }
        else:
            return {
                'SEO': 15, 'PAID_SEARCH': 25, 'PAID_SOCIAL': 20, 'CONTENT_MARKETING': 10,
                'EMAIL_MARKETING': 8, 'INFLUENCER': 5, 'PR': 5, 'EVENTS': 5, 'AFFILIATE': 4,
                'LLM_OPTIMIZATION': 3
            }

    def _apply_goal_adjustments(self, base_allocation, primary_goal, secondary_goals):
        adjusted = base_allocation.copy()
        
        goal_adjustments = {
            'LOW_COST_ACQUISITION': {
                'SEO': +15, 'CONTENT_MARKETING': +10, 'PAID_SEARCH': -10, 'PAID_SOCIAL': -10,
                'LLM_OPTIMIZATION': -5
            },
            'PRODUCT_VALIDATION': {
                'PAID_SEARCH': +15, 'PAID_SOCIAL': +15, 'INFLUENCER': +5, 'SEO': -10,
                'EMAIL_MARKETING': -5, 'LLM_OPTIMIZATION': -10
            },
            'LLM_VISIBILITY': {
                'LLM_OPTIMIZATION': +25, 'CONTENT_MARKETING': +10, 'SEO': +5, 'PAID_SEARCH': -10,
                'PAID_SOCIAL': -10, 'EMAIL_MARKETING': -5
            },
            'BRAND_AWARENESS': {
                'PAID_SOCIAL': +15, 'INFLUENCER': +10, 'PR': +10, 'SEO': -5, 'EMAIL_MARKETING': -10
            },
            'RAPID_GROWTH': {
                'PAID_SEARCH': +20, 'PAID_SOCIAL': +15, 'AFFILIATE': +5, 'SEO': -15,
                'CONTENT_MARKETING': -10
            },
            'LEAD_GENERATION': {
                'PAID_SEARCH': +15, 'EMAIL_MARKETING': +10, 'EVENTS': +5, 'SEO': -5,
                'LLM_OPTIMIZATION': -10
            }
        }
        
        if primary_goal in goal_adjustments:
            for channel, adjustment in goal_adjustments[primary_goal].items():
                adjusted[channel] += adjustment
        
        for goal in secondary_goals:
            if goal in goal_adjustments:
                for channel, adjustment in goal_adjustments[goal].items():
                    adjusted[channel] += adjustment * 0.5
        
        for channel in adjusted:
            adjusted[channel] = max(0, adjusted[channel])
        
        return adjusted

    def _normalize_allocation(self, allocation, total_budget):
        total_percentage = sum(allocation.values())
        
        if total_percentage == 0:
            return {}
        
        normalized = {}
        for channel, percentage in allocation.items():
            normalized_percentage = (percentage / total_percentage) * 100
            dollar_amount = (normalized_percentage / 100) * total_budget
            
            normalized[channel] = {
                'percentage': round(normalized_percentage, 1),
                'amount': round(dollar_amount, 2),
                'description': self.channels[channel]
            }
        
        return normalized

# Google Sheets Integration
def connect_to_google_sheets(credentials_json):
    """Connect to Google Sheets using service account credentials"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(credentials_json, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def get_industry_data(client, spreadsheet_url, industry=None):
    """Get industry-specific allocation data from Google Sheets"""
    try:
        sheet = client.open_by_url(spreadsheet_url)
        worksheet = sheet.sheet1  # or specify your worksheet name
        
        # Get all data
        data = worksheet.get_all_records()
        
        if industry and data:
            # Filter by industry if specified
            industry_data = next((row for row in data if row.get('industry', '').lower() == industry.lower()), None)
            if industry_data:
                return industry_data
        
        return data[0] if data else None  # Return first row as default
        
    except Exception as e:
        st.error(f"Error reading from Google Sheets: {e}")
        return None

def main():
    # Main header with custom styling
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("💰 Marketing Budget Allocation Calculator")
    st.markdown("### Data-Driven Budget Planning for Client Marketing Campaigns")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize calculator
    calculator = MarketingBudgetCalculator()
    
    # Sidebar for configuration with depth styling
    with st.sidebar:
        st.markdown('<div class="custom-header">⚙️ Configuration</div>', unsafe_allow_html=True)
        
        # Google Sheets Integration
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Google Sheets Integration")
        use_google_sheets = st.checkbox("Connect to Google Sheets", value=False)
        
        if use_google_sheets:
            st.info("To use Google Sheets integration, you'll need to:")
            st.markdown("""
            1. Create a Google Sheet with your industry data
            2. Set up a Google Service Account
            3. Share your sheet with the service account email
            """)
            
            spreadsheet_url = st.text_input("Google Sheet URL", placeholder="https://docs.google.com/spreadsheets/d/...")
            credentials_json = st.text_area("Service Account JSON", placeholder='{"type": "service_account", ...}', height=200)
            
            industry = st.selectbox("Industry (optional)", 
                                  ["", "SaaS", "E-commerce", "B2B", "Consumer Goods", "Healthcare", "Finance"])
        else:
            spreadsheet_url = None
            credentials_json = None
            industry = None
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main calculator interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("📊 Input Parameters")
        
        # Budget input
        budget = st.number_input(
            "Total Marketing Budget ($)",
            min_value=1000,
            max_value=1000000,
            value=50000,
            step=1000,
            help="Enter the total budget for the marketing campaign"
        )
        
        # Goal selection
        primary_goal = st.selectbox(
            "Primary Marketing Goal",
            options=list(calculator.goals.keys()),
            format_func=lambda x: calculator.goals[x],
            help="Select the main objective for this campaign"
        )
        
        # Secondary goals
        secondary_goals = st.multiselect(
            "Secondary Goals (optional)",
            options=list(calculator.goals.keys()),
            format_func=lambda x: calculator.goals[x],
            help="Select additional objectives to consider"
        )
        
        # Calculate button
        calculate_btn = st.button("🚀 Calculate Optimal Allocation", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("ℹ️ About This Calculator")
        st.markdown("""
        This tool helps you allocate marketing budgets based on:
        
        - **Client Goals**: Different objectives require different channel mixes
        - **Budget Size**: Allocation strategies vary by budget tier
        - **Industry Data**: Optional integration with your Google Sheets data
        - **Historical Performance**: Data-driven recommendations
        
        **Supported Goals:**
        - Low Cost Acquisition (SEO-heavy)
        - Product Validation (Paid channels)
        - LLM Visibility (Content + SEO)
        - Brand Awareness (Social + PR)
        - Rapid Growth (Paid acquisition)
        - Lead Generation (Search + Email)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate and display results
    if calculate_btn:
        st.markdown('<div class="custom-header">🎯 Recommended Allocation</div>', unsafe_allow_html=True)
        
        # Get industry data if Google Sheets is connected
        industry_data = None
        if use_google_sheets and spreadsheet_url and credentials_json:
            try:
                credentials_dict = json.loads(credentials_json)
                client = connect_to_google_sheets(credentials_dict)
                if client:
                    industry_data = get_industry_data(client, spreadsheet_url, industry)
                    if industry_data:
                        st.success(f"✅ Using industry data for: {industry if industry else 'Default'}")
            except Exception as e:
                st.error(f"Failed to load industry data: {e}")
        
        # Calculate allocation
        with st.spinner("Calculating optimal allocation..."):
            allocation = calculator.calculate_allocation(
                budget, primary_goal, secondary_goals, industry_data
            )
        
        # Display results in columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="results-table">', unsafe_allow_html=True)
            st.subheader("Budget Breakdown")
            
            # Create results table
            results_data = []
            for channel, data in allocation.items():
                if data['percentage'] > 0:
                    results_data.append({
                        'Channel': data['description'],
                        'Percentage': f"{data['percentage']}%",
                        'Amount': f"${data['amount']:,.2f}"
                    })
            
            # Sort by percentage descending
            results_data.sort(key=lambda x: float(x['Percentage'].replace('%', '')), reverse=True)
            
            # Display as table
            st.dataframe(
                pd.DataFrame(results_data),
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-container">', unsafe_allow_html=True)
            st.subheader("Quick Stats")
            
            # Calculate some stats
            total_allocated = sum(data['amount'] for data in allocation.values())
            top_channel = max(allocation.items(), key=lambda x: x[1]['percentage'])
            
            st.metric("Total Budget", f"${budget:,.0f}")
            st.metric("Total Allocated", f"${total_allocated:,.0f}")
            st.metric("Top Channel", f"{top_channel[1]['description']} ({top_channel[1]['percentage']}%)")
            
            # Channel type breakdown
            organic_channels = ['SEO', 'CONTENT_MARKETING', 'EMAIL_MARKETING', 'PR']
            paid_channels = ['PAID_SEARCH', 'PAID_SOCIAL', 'INFLUENCER', 'AFFILIATE']
            
            organic_percent = sum(allocation[ch]['percentage'] for ch in organic_channels if ch in allocation)
            paid_percent = sum(allocation[ch]['percentage'] for ch in paid_channels if ch in allocation)
            
            st.metric("Organic Channels", f"{organic_percent:.1f}%")
            st.metric("Paid Channels", f"{paid_percent:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export options
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📤 Export Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as CSV
            df = pd.DataFrame([
                {
                    'Channel': data['description'],
                    'Percentage': data['percentage'],
                    'Amount': data['amount']
                }
                for data in allocation.values() if data['percentage'] > 0
            ])
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download as CSV",
                data=csv,
                file_name=f"marketing_allocation_{budget}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Copy to clipboard
            if st.button("📋 Copy to Clipboard"):
                allocation_text = "\n".join([
                    f"{data['description']}: {data['percentage']}% (${data['amount']:,.2f})"
                    for data in allocation.values() if data['percentage'] > 0
                ])
                st.code(allocation_text)
        
        with col3:
            # Save to Google Sheets
            if use_google_sheets and st.button("💾 Save to Google Sheets"):
                st.info("This would save the results back to your Google Sheet")
                # Implementation for saving back to sheets would go here
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

