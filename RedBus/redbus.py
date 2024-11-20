import streamlit as st
import pymysql
import pandas as pd

# Connect to MySQL database
def get_connection():
    return pymysql.connect(host='127.0.0.1', user='root', password='Ragini95@', database='redbus')

# Fetch  route names based on the input name
def fetch_route_names(myconnection, name):
    query = "select distinct  Route_Name from bus_routes where Route_Name like %s order by Route_Name"
    with myconnection.cursor() as cursor:
        cursor.execute(query, (f"{name}%",))
        route_names = [row[0] for row in cursor.fetchall()]
    return route_names

# Fetch data based on selected Route_Name and price sorting order
def fetch_data(myconnection, route_name, price_order):
    price_sql = "ASC" if price_order == "Low to High" else "DESC"
    query = f"select * from bus_routes where Route_Name = %s order by Star_Rating DESC, Price {price_sql}"
   
    with myconnection.cursor() as cursor:
        cursor.execute(query, (route_name,))
        # Fetch all rows and convert to DataFrame
        data = cursor.fetchall()
        # Get column names for DataFrame
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(data, columns=columns)

# Filter data based on star ratings and bus types
def filter_data(data, selected_ratings, selected_bus_types):
    filtered_data = data[(data['Star_Rating']==(selected_ratings)) & (data['Bus_Type']==(selected_bus_types))]
    return filtered_data
def add_background_color():
    st.markdown(
        """
        <style>
        .main {
            background-color:#f08080; /* dark peach */
            
        }
        </style>
        """,
        unsafe_allow_html=True
    )
def main():
    add_background_color()

    st.header('Comfort Travel with RedBus.COM')
    st.title("RedBus.com")

    myconnection = get_connection()
    try:
        # Sidebar - input for route name's first letter
        name = st.sidebar.text_input('Enter First Letter of Route Name (e.g., A, B)')
        if name:
            route_names = fetch_route_names(myconnection, name.upper())
            if route_names:
                # Sidebar - Radio button to select a route name
                selected_route = st.sidebar.radio('Select Route Name', route_names)

                if selected_route:
                    # Sidebar - Select box for price sorting preference
                    price_order = st.sidebar.selectbox('Sort by Price', ['Low to High', 'High to Low'])

                    # Fetch data for the selected route and price order
                    data = fetch_data(myconnection, selected_route, price_order)

                    if not data.empty:
                        # Display the selected route name
                        st.write(f"### Route Name: {selected_route}")

                        # Sidebar - Filters for star ratings and bus types
                        star_ratings = sorted(data['Star_Rating'].unique().tolist())
                        selected_ratings = st.sidebar.selectbox('Select Star Rating(s)', star_ratings)

                        bus_types = sorted(data['Bus_Type'].unique().tolist())
                        selected_bus_types = st.sidebar.selectbox('Select Bus Type(s)', bus_types)

                        # Display the fetched data
                        st.write("### Bus Data")
                        st.write(data)
                        button = st.sidebar.button("SEARCH")

                        # Apply filters and display the filtered data when "SEARCH" button is clicked
                        if selected_ratings and selected_bus_types:
                            if button:
                                # Apply filters and display the filtered data
                                filtered_data = filter_data(data, selected_ratings, selected_bus_types)
                                st.write("### Filtered Results")
                                st.write(filtered_data)
                            book = st.button("Book Now") #Book the bus when "Book Now" button is clicked
                            if book:
                                st.write("### Booking Successfully")

                
                        else:
                            st.write("Please select both Star Ratings and Bus Types to apply filters.")
                    else:
                        st.write(f"No data found for Route: {selected_route} with the specified price sorting order.")
                else:
                    st.write("No route selected.")
            else:
                st.write("No routes found starting with the specified letter.")
        else:
            st.write("Please enter the first letter of the route name.")
    finally:
        myconnection.close()

if __name__ == '__main__':
    main()
