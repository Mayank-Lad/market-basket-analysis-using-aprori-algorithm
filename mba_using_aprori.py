import pandas as pd
import streamlit as st
from apyori import apriori
import networkx as nx
import threading
import time
df=pd.read_csv("dataset/store_data.csv",header=None)#### this is done  as the first transition done is gone to header
# Streamlit app
st.title("Product Association Platform")

st.markdown("If Transactions are properly analysed then Business Growth is ")

images = ["images/analytics.jpg", "images/growth.jpg"]

current_image_index = 0

image_container = st.empty()

image_container.image(images[current_image_index])
  
def while_loop_function():
    current_image_index = 0
    while True:

        st.session_state.current_image_index = current_image_index
        image_container.image(images[current_image_index])

        current_image_index += 1

        current_image_index %= len(images)
        time.sleep(5)


st.dataframe(df)
df.fillna(0,inplace=True)
selected_product = st.sidebar.selectbox("Select a Product", df[0].unique())

transactions = []
for i in range(0,len(df)):
    transactions.append([str(df.values[i,j]) for j in range(0,20) if str(df.values[i,j])!='0'])

rules = apriori(transactions, min_support=0.003, min_confidence=0.2, min_lift=3, min_length=2)
results = list(rules)

# Recommend products based on user selection
recommended_products = []

for item in results:
    pair = item[0]
    items = [x for x in pair]
    if selected_product in items:
        other_product = items[1] if items[0] == selected_product else items[0]
        support = item[1]
        confidence = item[2][0][2]
        recommended_products.append((other_product, support, confidence))

# Filter out NaN values and sort based on confidence and support
recommended_products = [(product, support, confidence) for product, support, confidence in recommended_products
                        if not pd.isna(product) and not pd.isna(support) and not pd.isna(confidence)]
recommended_products = [(product, support, confidence) if not pd.isna(product) and not pd.isna(support) and not pd.isna(confidence)
                        else (product, 0, 0) for product, support, confidence in recommended_products]

recommended_products.sort(key=lambda x: (x[1], x[2]), reverse=True)

unique_recommended_products = set()
top_recommended_products = []

for product, support, confidence in recommended_products:
    if product not in unique_recommended_products:
        unique_recommended_products.add(product)
        top_recommended_products.append((product, support, confidence))
    if len(top_recommended_products) == 3:
        break

st.header("Top 3 Recommended Products")
if(len(top_recommended_products)>0):
  for idx, (product, support, confidence) in enumerate(top_recommended_products):
      st.write(f"Rank {idx + 1}:")
      if(idx+1==1):
        highestrankedprod=product
      st.write(f"Product: {product}")
      st.write(f"Support: {support}")
      st.write(f"Confidence: {confidence}")
      st.write("-----")    
      
else:
    st.write("No Recommendations for the Selected Product")

if(len(top_recommended_products)>0):
  st.subheader("Inference")
  st.write("The Product "+selected_product+" is Highly Associated with "+highestrankedprod+" they should be kept together to increase the sales ")
st.header("Product Support Visualization")
product_support_df = pd.DataFrame([(item[0], item[1]) for item in results], columns=["Product", "Support"])
st.bar_chart(product_support_df.set_index("Product"))

st.header("Confidence vs. Support")
scatter_df = pd.DataFrame([(item[1], item[2][0][2]) for item in results], columns=["Support", "Confidence"])
st.scatter_chart(scatter_df)

st.header("Lift vs. Support")
lift_df = pd.DataFrame([(item[1], item[2][0][3]) for item in results], columns=["Support", "Lift"])
st.scatter_chart(lift_df)
while_loop_thread = threading.Thread(target=while_loop_function())


