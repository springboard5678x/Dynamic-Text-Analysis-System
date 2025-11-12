import requests
import json
import os
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_api_connection():
    """Test if API is accessible"""
    print("🔌 Testing API connection...")
    try:
        response = requests.get(f"{BASE_URL}/analysis/")
        if response.status_code == 200:
            print("✅ API is accessible and working!")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_text_analysis():
    """Test text analysis with raw text input"""
    print("\n📝 Testing Text Analysis with Raw Text...")
    
    sample_text = """
    Customer feedback analysis reveals several key points about our new product launch. 
    Users are generally very satisfied with the improved user interface and faster performance. 
    However, there are consistent complaints about the battery life and heating issues. 
    Many customers have expressed disappointment with the limited color options available. 
    The camera quality receives mixed reviews, with some praising the low-light performance 
    while others find it inconsistent. Overall, the product shows promise but needs 
    immediate attention to hardware issues and expanded customization options.
    
    Positive aspects mentioned by customers include the sleek design, intuitive navigation, 
    and excellent customer support. Negative feedback primarily focuses on technical 
    limitations and lack of variety in product choices. The marketing campaign was successful 
    in generating initial interest, but product quality concerns are affecting retention rates.
    Customer service responsiveness has been praised, though some users report long wait times 
    during peak hours. The mobile application companion receives positive feedback for its 
    feature set but needs optimization for better performance on older devices.
    
    Technical specifications meet industry standards, but user experience could be enhanced 
    through software updates addressing the reported issues. The development team is actively 
    working on solutions for the most critical problems mentioned in user feedback.
    """
    
    payload = {
        "title": f"Customer Feedback Analysis - {datetime.now().strftime('%H:%M:%S')}",
        "input_text": sample_text
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analysis/", json=payload)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Text Analysis Successful!")
            print(f"📊 Analysis ID: {data['id']}")
            print(f"📋 Title: {data['title']}")
            return data['id']
        else:
            print(f"❌ Text Analysis Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during text analysis: {e}")
        return None

def test_file_analysis():
    """Test analysis with file upload"""
    print("\n📁 Testing File Analysis...")
    
    # Create a sample text file with more content
    sample_file_content = """
    Quarterly Performance Report Q3 2024
    
    The company demonstrated strong growth in the third quarter with revenue increasing by 15% 
    compared to the same period last year. Customer acquisition rates improved significantly, 
    showing a 25% increase in new subscriptions. However, customer retention remains a concern 
    with churn rates increasing by 5%. 
    
    Employee satisfaction surveys indicate high morale among technical teams but reveal 
    concerns about work-life balance in the sales department. The marketing campaign 
    launched in August received positive feedback and generated substantial brand awareness.
    
    Key challenges identified include supply chain disruptions and increased competition 
    in the European market. Strategic recommendations focus on diversifying suppliers 
    and enhancing customer loyalty programs.
    
    Financial performance exceeded expectations with net profit margins improving by 8%. 
    The research and development department successfully launched two new product features 
    that have been well-received by early adopters. Market expansion initiatives in Asia 
    show promising early results with a 30% increase in market share.
    
    Operational efficiency improved through the implementation of new automation tools, 
    reducing manual processing time by 40%. Customer support metrics show improved 
    response times but indicate a need for additional training on complex technical issues.
    
    Looking forward to Q4, the company plans to focus on customer retention strategies 
    and product innovation to maintain competitive advantage in the market.
    """
    
    # Create test file with unique name to avoid conflicts
    file_path = f"test_report_{datetime.now().strftime('%H%M%S')}.txt"
    
    try:
        # Write file first
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sample_file_content)
        
        # Close the file and reopen for reading to avoid permission issues
        file_obj = None
        try:
            file_obj = open(file_path, "rb")
            files = {
                'uploaded_file': file_obj
            }
            data = {
                'title': f'Quarterly Report Analysis - {datetime.now().strftime("%H:%M:%S")}'
            }
            
            response = requests.post(f"{BASE_URL}/analysis/", files=files, data=data)
        
            if response.status_code == 201:
                data = response.json()
                print("✅ File Analysis Successful!")
                print(f"📊 Analysis ID: {data['id']}")
                print(f"📁 File Type: {data.get('file_type', 'N/A')}")
                return data['id']
            else:
                print(f"❌ File Analysis Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        finally:
            if file_obj:
                file_obj.close()
            
    except Exception as e:
        print(f"❌ Error during file analysis: {e}")
        return None
    finally:
        # Clean up test file with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    break
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # Wait 100ms before retry
                else:
                    print(f"⚠️ Could not delete test file after {max_retries} attempts: {file_path}")

def get_analysis_results(analysis_id):
    """Retrieve and display analysis results"""
    print(f"\n📈 Retrieving Results for Analysis {analysis_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/analysis/{analysis_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Results Retrieved Successfully!")
            
            # Display key results
            print(f"\n🎯 Analysis Summary:")
            print(f"   Title: {data['title']}")
            print(f"   Created: {data['created_at']}")
            
            # Topics
            if data.get('topics_json'):
                print(f"\n📊 Topics Identified:")
                for topic in data['topics_json'][:3]:  # Show first 3 topics
                    words = ', '.join(topic['words'][:5])
                    print(f"   Topic {topic['topic_id']}: {words}")
            
            # Sentiment
            if data.get('sentiment_distribution'):
                sentiment = data['sentiment_distribution']
                print(f"\n😊 Sentiment Analysis:")
                print(f"   Overall: {sentiment.get('overall_sentiment', 'N/A')}")
                if 'distribution' in sentiment:
                    dist = sentiment['distribution']
                    total = sum(dist.values())
                    if total > 0:
                        print(f"   Positive: {dist.get('positive', 0)} ({dist.get('positive', 0)/total*100:.1f}%)")
                        print(f"   Neutral: {dist.get('neutral', 0)} ({dist.get('neutral', 0)/total*100:.1f}%)")
                        print(f"   Negative: {dist.get('negative', 0)} ({dist.get('negative', 0)/total*100:.1f}%)")
            
            # Summaries
            if data.get('extractive_summary'):
                print(f"\n📋 Extractive Summary (first 120 chars):")
                print(f"   {data['extractive_summary'][:120]}...")
            
            if data.get('abstractive_summary'):
                print(f"\n📝 Abstractive Summary (first 120 chars):")
                print(f"   {data['abstractive_summary'][:120]}...")
            
            # Insights
            if data.get('actionable_insights'):
                print(f"\n💡 Actionable Insights:")
                for insight in data['actionable_insights'][:2]:
                    print(f"   • {insight['title']}: {insight['recommendation']}")
            
            return True
        else:
            print(f"❌ Failed to retrieve results: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving results: {e}")
        return False

def download_report(analysis_id):
    """Test report download functionality"""
    print(f"\n📄 Testing Report Download for {analysis_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/analysis/{analysis_id}/download_report/")
        
        if response.status_code == 200:
            # Save the report file
            report_filename = f"report_{analysis_id}.pdf"
            with open(report_filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Report Downloaded Successfully: {report_filename}")
            return True
        else:
            print(f"❌ Report download failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading report: {e}")
        return False

def list_all_analyses():
    """List all existing analyses"""
    print("\n📋 Listing All Analyses...")
    
    try:
        response = requests.get(f"{BASE_URL}/analysis/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Total Analyses: {len(data)}")
            for analysis in data[:3]:  # Show first 3 only
                print(f"   • {analysis['title']} - {analysis['created_at']}")
            if len(data) > 3:
                print(f"   ... and {len(data) - 3} more")
            return True
        else:
            print(f"❌ Failed to list analyses: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error listing analyses: {e}")
        return False

def main():
    """Run complete API test suite"""
    print("🚀 Starting NarrativeNexus API Test Suite")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        print("Stopping tests due to API connection failure")
        return
    
    # Test 1: Text Analysis
    print("\n" + "="*30)
    print("TEST 1: TEXT ANALYSIS")
    print("="*30)
    text_analysis_id = test_text_analysis()
    if text_analysis_id:
        get_analysis_results(text_analysis_id)
        download_report(text_analysis_id)
    
    # Test 2: File Analysis  
    print("\n" + "="*30)
    print("TEST 2: FILE ANALYSIS")
    print("="*30)
    file_analysis_id = test_file_analysis()
    if file_analysis_id:
        get_analysis_results(file_analysis_id)
        download_report(file_analysis_id)
    
    # List all analyses
    print("\n" + "="*30)
    print("FINAL OVERVIEW")
    print("="*30)
    list_all_analyses()
    
    print("\n" + "=" * 50)
    print("🎉 API Test Suite Completed!")
    print("\n📝 Next Steps:")
    print("   • Check the Django admin at http://localhost:8000/admin/")
    print("   • View generated PDF reports in the media/generated_reports/ folder")
    print("   • Start building the React frontend!")

if __name__ == "__main__":
    main()