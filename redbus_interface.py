import streamlit as st
import pymysql
import pandas as pd
from datetime import date

# Connect to MySQL database
def get_connection():
    try:
        return pymysql.connect(
            host='127.0.0.1', 
            user='root', 
            password='Ragini95@', 
            database='redbus_project'
        )
    except pymysql.MySQLError as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Fetch available routes based on state
def fetch_routes(myconnection, state_name):
    query = """
        SELECT DISTINCT Route_Name
        FROM redbus_details 
        WHERE State_Name = %s 
        ORDER BY Route_Name
    """
    try:
        with myconnection.cursor() as cursor:
            cursor.execute(query, (state_name,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    except pymysql.MySQLError as e:
        st.error(f"Error fetching routes: {e}")
        return []

# Fetch bus data for the selected route
def fetch_data(myconnection, selected_route, bus_category, ac_category):
    query = """
        SELECT Route_Name, Route_Link, Bus_Name, Bus_Type, Departing_Time, Reaching_Time, Duration,
               COALESCE(Price, 'Not Available') AS Price, 
               COALESCE(Star_Rating, 0) AS Star_Rating  
        FROM redbus_details 
        WHERE Route_Name = %s AND Bus_Category = %s AND AC_Category = %s 
        ORDER BY Star_Rating DESC
    """
    try:
        with myconnection.cursor() as cursor:
            cursor.execute(query, (selected_route, bus_category, ac_category))
            data = cursor.fetchall()
            if data:
                column_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(data, columns=column_names)

                # Convert 'Price' to numeric for filtering and sorting
                df['Price'] = pd.to_numeric(
                    df['Price'].str.replace('INR', '').str.strip(), 
                    errors='coerce'
                )

                return df
            else:
                return pd.DataFrame()
    except pymysql.MySQLError as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Filter data based on user inputs
def filter_data(data, price_range, rating_range):
    # Ensure 'Price' and 'Star_Rating' are numeric
    data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
    data['Star_Rating'] = pd.to_numeric(data['Star_Rating'], errors='coerce')

    # Apply filters
    filtered_data = data[
        (data['Price'] >= price_range[0]) & 
        (data['Price'] <= price_range[1]) &
        (data['Star_Rating'] >= rating_range[0]) & 
        (data['Star_Rating'] <= rating_range[1])
    ]
    return filtered_data
def add_background_color():
    st.markdown(
        """
        <style>
        .main {
            background-color:#f58f0a; /* dark peach */
            
        }
        </style>
        """,
        unsafe_allow_html=True
    )
# Main Streamlit application
def main():
    add_background_color()
    st.header('Comfort Travel with RedBus.COM')
    st.title("RedBus.com")

    # Connect to the database
    myconnection = get_connection()
    if myconnection is None:
        st.stop()

    try:
        selected_date = st.sidebar.date_input("Select Travel Date", date.today())
        state_name = st.sidebar.selectbox(
            'Select State',
            ['Andhra Pradesh', 'Kerala', 'Telangana', 'Rajasthan', 'South Bengal',
             'Himachal Pradesh', 'Assam', 'Uttar Pradesh', 'Kadamba', 'West Bengal', 'Chandigarh', 'Punjab']
        )
        bus_category = st.sidebar.radio('Select Bus Category', ['Government Bus', 'Private Bus'])
        ac_category = st.sidebar.selectbox('Select Bus Type', [
            'AC', 'AC SLEEPER', 'AC SEATER', 
            'NON-AC', 'NON-AC SLEEPER', 'NON-AC SEATER'
        ])

        if state_name:
            routes = fetch_routes(myconnection, state_name)
            if routes:
                selected_route = st.sidebar.selectbox('Select Route Name', sorted(routes))
                
                if selected_route:
                    st.sidebar.markdown("### Filter by Price")
                    price_range = st.sidebar.slider('Price Range (in INR)', 100, 5000, (100, 3000), step=100)

                    st.sidebar.markdown("### Filter by Star Rating")
                    rating_range = st.sidebar.slider('Star Rating Range', 1, 5, (1, 5), step=1)

                    data = fetch_data(myconnection, selected_route, bus_category, ac_category)

                    if not data.empty:
                        st.write(f"### Route: {selected_route}")
                        st.write("#### Available Buses")
                        st.write(data)

                        if st.sidebar.button("SEARCH"):
                            filtered_data = filter_data(data, price_range, rating_range)

                            st.write("### Filtered Results")
                            if not filtered_data.empty:
                                st.write(filtered_data)
                            else:
                                st.write("### No buses match the selected filters.")
                    else:
                        st.write("### No buses found matching your criteria.Please select other BUS Type.")
            else:
                st.write("### No routes found for the selected state.")
    finally:
        myconnection.close()

if __name__ == '__main__':
    main()
