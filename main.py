import streamlit as st
import mysql.connector
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
mydb = mysql.connector.connect(host="localhost",
                             user="root",
                             database="cms")
cursor = mydb.cursor()




def check_login(username, password):
   cursor.execute(
       "SELECT * FROM user WHERE username = %s AND password_ = %s",
       (username, password))
   return cursor.fetchone()


def get_user_role(user_id):
   cursor.execute("SELECT role FROM user WHERE user_id = %s",
                  (user_id, ))
   result = cursor.fetchone()
   return result[0] if result else None


def logout():
   st.session_state.clear()


def login():
   username = st.text_input("Username")
   password = st.text_input("Password", type="password")
   if st.button("Login"):
       user = check_login(username, password)
       if user:
           st.session_state['user_id'] = user[0]
           st.session_state['role'] = get_user_role(user[0])
           st.session_state['logged_in'] = True
           st.success("Logged in successfully!")
       else:
           st.error("Invalid username or password.")


def add_customer(name, email_id, contact, poc, poc_email, address, website):
   sql = """
   INSERT INTO customer (name, email_id, contact, poc, poc_email, address, website)
   VALUES (%s, %s, %s, %s, %s, %s, %s)
   """
   values = (name, email_id, contact, poc, poc_email, address, website)
   cursor.execute(sql, values)
   mydb.commit()
   st.success("Customer added successfully!")


def get_all_customers():
   cursor.execute("SELECT * FROM customer")
   customers = cursor.fetchall()
   return customers


def edit_customer_poc(customer_id, new_poc, new_poc_email):
   sql = "UPDATE customer SET poc = %s, poc_email = %s WHERE customer_id = %s"
   values = (new_poc, new_poc_email, customer_id)
   cursor.execute(sql, values)
   mydb.commit()
   st.success("Customer POC updated successfully!")


def delete_customer(customer_id):
   sql = "DELETE FROM customer WHERE customer_id = %s"
   cursor.execute(sql, (customer_id,))
   mydb.commit()
   st.warning("Customer deleted successfully!")


def add_lead(name, email_id, contact, poc, poc_email, address, status, lead_source, last_follow_up_date, notes):
   sql = """
   INSERT INTO leads (name, email_id, contact, poc, poc_email, address, status, lead_source, last_follow_up_date, notes)
   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
   """
   values = (name, email_id, contact, poc, poc_email, address, status, lead_source, last_follow_up_date, notes)
   cursor.execute(sql, values)
   mydb.commit()
   st.success("Lead added successfully!")


def update_lead_status(lead_id, new_status):
   sql = "UPDATE leads SET status = %s WHERE lead_id = %s"
   cursor.execute(sql, (new_status, lead_id))
   mydb.commit()
   st.success("Lead status updated successfully!")


def update_lead_poc(lead_id, new_poc, new_poc_email):
   sql = "UPDATE leads SET poc = %s, poc_email = %s WHERE lead_id = %s"
   cursor.execute(sql, (new_poc, new_poc_email, lead_id))
   mydb.commit()
   st.success("Lead POC updated successfully!")


def update_lead_notes(lead_id, new_notes):
   sql = "UPDATE leads SET notes = %s WHERE lead_id = %s"
   cursor.execute(sql, (new_notes, lead_id))
   mydb.commit()
   st.success("Lead notes updated successfully!")


def fetch_leads():
   cursor.execute("SELECT * FROM leads")
   data = cursor.fetchall()
   return data


def schedule_followup(status, meetlink, followup_time, assignee, entity_type, entity_id, comments):
   query = """INSERT INTO followups (status, meetlink, followup_time, assignee, entity_type, entity_id, comments)
              VALUES (%s, %s, %s, %s, %s, %s, %s)"""
   cursor.execute(query, (status, meetlink, followup_time, assignee, entity_type, entity_id, comments))
   mydb.commit()
   st.success("Follow-up scheduled successfully!")




def update_followup_status_and_comments(followup_id, new_status, new_comments, current_user):
   cursor.execute("SELECT entity_type, entity_id FROM followups WHERE followup_id = %s AND assignee = %s",
                  (followup_id, current_user))
   result = cursor.fetchone()


   if result:
       entity_type, entity_id = result
       query = """UPDATE followups SET status = %s, comments = %s WHERE followup_id = %s AND assignee = %s"""
       cursor.execute(query, (new_status, new_comments, followup_id, current_user))
       if entity_type == "lead":
           cursor.execute("UPDATE leads SET last_follow_up_date = NOW() WHERE lead_id = %s", (entity_id,))
       mydb.commit()
       st.success("Follow-up status and comments updated successfully! (Lead's last follow-up date updated if applicable)")
   else:
       st.error("Update failed! Either the follow-up ID is invalid or you are not the assignee.")


def update_followup_assignee(followup_id, new_assignee):
   query = """UPDATE followups SET assignee = %s WHERE followup_id = %s"""
   cursor.execute(query, (new_assignee, followup_id))
   mydb.commit()
   st.success("Follow-up assignee updated successfully!")


def get_followups_by_entity(entity_type, entity_id):
   query = """SELECT * FROM followups WHERE entity_type = %s AND entity_id = %s"""
   cursor.execute(query, (entity_type, entity_id))
   data = cursor.fetchall()
   return data


def get_followups_by_assignee(assignee):
   query = """SELECT * FROM followups WHERE assignee = %s"""
   cursor.execute(query, (assignee,))
   data = cursor.fetchall()
   return data


def create_product(product_name, description, cost_price, selling_price, stock_quantity):
   query = """INSERT INTO Product (product_name, description, review, cost_price, selling_price, stock_quantity)
              VALUES (%s, %s, NULL, %s, %s, %s)"""
   cursor.execute(query, (product_name, description, cost_price, selling_price, stock_quantity))
   mydb.commit()
   st.success("Product created successfully!")


def update_stock_quantity(product_id, new_stock):
   query = "UPDATE Product SET stock_quantity = %s WHERE product_id = %s"
   cursor.execute(query, (new_stock, product_id))
   mydb.commit()
   st.success("Stock quantity updated successfully!")


def delete_product(product_id):
   query = "DELETE FROM Product WHERE product_id = %s"
   cursor.execute(query, (product_id,))
   mydb.commit()
   st.success("Product deleted successfully!")


def view_products():
   query = "SELECT * FROM Product"
   cursor.execute(query)
   data = cursor.fetchall()
   if data:
       df = pd.DataFrame(data, columns=["Product ID", "Name", "Description", "Review", "Cost Price", "Selling Price", "Stock Quantity"])
       st.dataframe(df)
   else:
       st.warning("No products available.")


def create_user(name, email, username, password_, address, phone_number, role):
   query = """INSERT INTO user (name, email, username, password_, address, phone_number, role)
              VALUES (%s, %s, %s, %s, %s, %s, %s)"""
   try:
       cursor.execute(query, (name, email, username, password_, address, phone_number, role))
       mydb.commit()
       st.success("User created successfully!")
   except mysql.connector.IntegrityError:
       st.error("Email or username already exists!")


def view_users():
   query = "SELECT user_id, name, email, username, address, phone_number, role, created_at FROM user"
   cursor.execute(query)
   data = cursor.fetchall()
   if data:
       df = pd.DataFrame(data, columns=["User ID", "Name", "Email", "Username", "Address", "Phone", "Role", "Created At"])
       st.dataframe(df)
   else:
       st.warning("No users found.")


def delete_user(user_id):
   query = "DELETE FROM user WHERE user_id = %s"
   cursor.execute(query, (user_id,))
   mydb.commit()
   st.success("User deleted successfully!")


def create_order(product_id, customer_id, user_id, quantity, total_amount, final_price, delivery_date):
   cursor.execute("SELECT stock_quantity FROM Product WHERE product_id = %s", (product_id,))
   stock = cursor.fetchone()
   if not stock or stock[0] < quantity:
       st.error("Not enough stock available to fulfill this order!")
       return False
   cursor.execute("UPDATE Product SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                          (quantity, product_id))
   query = """INSERT INTO Orders (product_id, customer_id, user_id, quantity, total_amount, final_price, delivery_date)
              VALUES (%s, %s, %s, %s, %s, %s, %s)"""
   cursor.execute(query, (product_id, customer_id, user_id, quantity, total_amount, final_price, delivery_date))
   mydb.commit()
   st.success("Order created successfully!")


def update_order_status(order_id, new_status):
   try:
       cursor.execute("UPDATE Orders SET status = %s WHERE order_id = %s", (new_status, order_id))
       mydb.commit()
       print("Order status updated successfully!")
       st.success("Order status updated successfully!")
       return True


   except mysql.connector.Error as err:
       return False


def update_payment_status(order_id, new_payment_status):
   query = "UPDATE Orders SET payment_status = %s WHERE order_id = %s"
   cursor.execute(query, (new_payment_status, order_id))
   mydb.commit()
   st.success("Payment status updated successfully!")


def update_delivery_date(order_id, new_delivery_date):
   query = "UPDATE Orders SET delivery_date = %s WHERE order_id = %s"
   cursor.execute(query, (new_delivery_date, order_id))
   mydb.commit()
   st.success("Delivery date updated successfully!")


def update_review(order_id, review):
   if review < 1 or review > 5:
       st.error("Review must be between 1 and 5!")
       return
   query = "UPDATE Orders SET review = %s WHERE order_id = %s"
   cursor.execute(query, (review, order_id))
   cursor.execute("SELECT product_id FROM Orders WHERE order_id = %s", (order_id,))
   product = cursor.fetchone()
   if not product:
       print("Order not found!")
       return False


   product_id = product[0]
   cursor.execute("SELECT AVG(review) FROM Orders WHERE product_id = %s AND review IS NOT NULL", (product_id,))
   avg_review = cursor.fetchone()[0]
   cursor.execute("UPDATE Product SET review = %s WHERE product_id = %s", (round(avg_review, 1), product_id))


   mydb.commit()
   st.success("Review updated successfully!")


def view_orders_by(field, value):
   query = f"SELECT * FROM Orders WHERE {field} = %s"
   cursor.execute(query, (value,))
   data = cursor.fetchall()
   if data:
       df = pd.DataFrame(data, columns=["Order ID", "Product ID", "Customer ID", "User ID", "Quantity", "Total Amount", "Final Price", "Order Date", "Delivery Date", "Status", "Review", "Payment Status"])
       st.dataframe(df)
   else:
       st.warning("No orders found.")


def view_orders():
   query = f"SELECT * FROM Orders"
   cursor.execute(query)
   data = cursor.fetchall()
   if data:
       df = pd.DataFrame(data, columns=["Order ID", "Product ID", "Customer ID", "User ID", "Quantity", "Total Amount", "Final Price", "Order Date", "Delivery Date", "Status", "Review", "Payment Status"])
       st.dataframe(df)
   else:
       st.warning("No orders found.")


def get_customer_names():
   query = "SELECT name FROM Customer"
   cursor.execute(query)
   customers = [row[0] for row in cursor.fetchall()]
   return customers


def get_sales_data():
   query = """
       SELECT p.product_name, SUM(o.total_amount) AS total_sales
       FROM Orders o
       JOIN Product p ON o.product_id = p.product_id
       WHERE o.status = 'Completed'
       GROUP BY p.product_name
       ORDER BY total_sales DESC
   """
   df = pd.read_sql(query, mydb)
   return df


def plot_sales_by_product():
   df = get_sales_data()
   if df.empty:
       st.warning("No sales data available!")
       return


   st.subheader("Total Sales per Product")
   fig, ax = plt.subplots(figsize=(10, 6))
   sns.barplot(x=df["product_name"], y=df["total_sales"], palette="viridis", ax=ax)
  
   ax.set_xlabel("Product ID")
   ax.set_ylabel("Total Sales")
   ax.set_title("Sales by Product ID")
   ax.set_xticklabels(df["product_name"], rotation=45, ha="right")
   ax.grid(axis="y", linestyle="--", alpha=0.7)
   st.pyplot(fig)


def get_sales_data_quantity():
   query = """
       SELECT p.product_name, SUM(o.quantity) AS total_quantity
       FROM Orders o
       JOIN Product p ON o.product_id = p.product_id
       WHERE o.status = 'Completed'
       GROUP BY p.product_name
       ORDER BY total_quantity DESC
   """
   df = pd.read_sql(query, mydb)
   return df


def plot_sales_by_product_quantity():
   df = get_sales_data_quantity()
   if df.empty:
       st.warning("No sales data available!")
       return


   st.subheader("Total Quantity per Product")
   fig, ax = plt.subplots(figsize=(10, 6))
   sns.barplot(x=df["product_name"], y=df["total_quantity"], palette="viridis", ax=ax)
  
   ax.set_xlabel("Product ID")
   ax.set_ylabel("Total Quanity")
   ax.set_title("Quantity by Product ID")
   ax.set_xticklabels(df["product_name"], rotation=45, ha="right")
   ax.grid(axis="y", linestyle="--", alpha=0.7)
   st.pyplot(fig)


def get_profit_data():
   query = """
       SELECT p.product_name,
              SUM((o.final_price * o.quantity) - (p.cost_price * o.quantity)) AS total_profit
       FROM Orders o
       JOIN Product p ON o.product_id = p.product_id
       WHERE o.status = 'Completed'
       GROUP BY p.product_name
       ORDER BY total_profit DESC
   """
   df = pd.read_sql(query, mydb)
   print(df)
   return df


def plot_profit_by_product():
   st.title("Profit by Product")
   df = get_profit_data()
   if df.empty:
       st.warning("No profit data available!")
       return


   st.subheader("Total Profit per Product")
   fig, ax = plt.subplots(figsize=(10, 6))
   sns.barplot(x="product_name", y="total_profit", hue="product_name", data=df, legend=False, palette="coolwarm", ax=ax)


   ax.set_xlabel("Product Name")
   ax.set_ylabel("Total Profit")
   ax.set_title("Profit by Product")
   ax.set_xticklabels(df["product_name"], rotation=45, ha="right")
   ax.grid(axis="y", linestyle="--", alpha=0.7)


   st.pyplot(fig)


def get_order_status_data():
   query = """
       SELECT payment_status, COUNT(*) AS order_count
       FROM Orders
       GROUP BY payment_status
   """
   df = pd.read_sql(query, mydb)
   return df


def plot_payment_status():
   st.title("Order Payment Status Summary")


   df = get_order_status_data()


   if df.empty:
       st.warning("⚠️ No order data available!")
       return


   st.subheader("Order Count by Payment Status")
   fig, ax = plt.subplots(figsize=(8, 5))
   sns.barplot(x="payment_status", y="order_count", hue="payment_status", data=df, legend=False, palette="coolwarm", ax=ax)


   ax.set_xlabel("Payment Status")
   ax.set_ylabel("Number of Orders")
   ax.set_title("Order Payment Status Distribution")
   ax.grid(axis="y", linestyle="--", alpha=0.7)
   st.pyplot(fig)


def get_sales_data_time():
   query = """
           SELECT order_date, total_amount
           FROM Orders
           WHERE status = 'Completed'
       """
   df = pd.read_sql(query, mydb)


   if df.empty:
       st.warning("No sales data found!")
       return df


   df['order_date'] = pd.to_datetime(df['order_date'])
   df['year'] = df['order_date'].dt.year
   df['month'] = df['order_date'].dt.month
   df['year_month'] = df['order_date'].dt.strftime('%Y-%m')
   sales_df = df.groupby('year_month', as_index=False).agg(
       total_sales=('total_amount', 'sum')
       )
   st.write("Processed Sales Data:", sales_df)
   return sales_df


def plot_sales_by_time():
   st.title("Monthly Sales Trend")
   df = get_sales_data_time()


   if df.empty:
       st.warning("No sales data available!")
       return


   df["year_month"] = pd.to_datetime(df["year_month"], format="%Y-%m")


   st.subheader("Sales Trend by Year & Month")
   fig, ax = plt.subplots(figsize=(10, 5))
   sns.lineplot(x=df["year_month"], y=df["total_sales"], marker="o", ax=ax, color="b")


   ax.set_xlabel("Year-Month")
   ax.set_ylabel("Total Sales")
   ax.set_title("Monthly Sales Trend")
   ax.grid(True, linestyle="--", alpha=0.7)
   plt.xticks(rotation=45)
   st.pyplot(fig)


def get_sales_data_year(year):
   query = """
           SELECT order_date, total_amount
           FROM Orders
           WHERE status = 'Completed'
       """
   df = pd.read_sql(query, mydb)


   if df.empty:
       st.warning("No sales data found!")
       return df


   df['order_date'] = pd.to_datetime(df['order_date'])
   df['year'] = df['order_date'].dt.year
   df['month'] = df['order_date'].dt.month
   year = int(year)  # Convert input year to integer
   df = df[df["year"] == year]
   # df.loc[df["year"] == year, :]
   df['year_month'] = df['order_date'].dt.strftime('%Y-%m')
   sales_df = df.groupby('year_month', as_index=False).agg(
       total_sales=('total_amount', 'sum')
       )
   # st.write("Processed Sales Data:", sales_df)
   return sales_df


def plot_sales_by_year(year):
   df = get_sales_data_year(year)
   if df.empty:
       st.warning("No sales data available!")
       return


   df["year_month"] = pd.to_datetime(df["year_month"], format="%Y-%m")


   st.subheader("Sales Trend by Year & Month - "+year)
   fig, ax = plt.subplots(figsize=(10, 5))
   sns.lineplot(x=df["year_month"], y=df["total_sales"], marker="o", ax=ax, color="b")


   ax.set_xlabel("Year-Month")
   ax.set_ylabel("Total Sales")
   ax.set_title("Year-Month Sales Trend"+year)
   ax.grid(True, linestyle="--", alpha=0.7)
   plt.xticks(rotation=45)
   st.pyplot(fig)


def get_sales_data_year1():
   query = """
           SELECT order_date, total_amount
           FROM Orders
           WHERE status = 'Completed'
       """
   df = pd.read_sql(query, mydb)


   if df.empty:
       st.warning("No sales data found!")
       return df


   df['order_date'] = pd.to_datetime(df['order_date'])
   df['year'] = df['order_date'].dt.year
   df['month'] = df['order_date'].dt.month
   sales_df = df.groupby('year', as_index=False).agg(
       total_sales=('total_amount', 'sum')
       )
   st.write("Processed Sales Data:", sales_df)
   return sales_df


def plot_sales_by_year1():
   df = get_sales_data_year1()
   if df.empty:
       st.warning("No sales data available!")
       return
   st.subheader("Sales Trend by Year & Month")
   fig, ax = plt.subplots(figsize=(10, 5))
   sns.lineplot(x=df["year"], y=df["total_sales"], marker="o", ax=ax, color="b")


   ax.set_xlabel("Year")
   ax.set_ylabel("Total Sales")
   ax.set_title("Yearly Sales Trend")
   ax.grid(True, linestyle="--", alpha=0.7)
   plt.xticks(rotation=45)
   st.pyplot(fig)


def plot_order_status_count():
   query = """
       SELECT status, COUNT(*) as count
       FROM Orders
       GROUP BY status
   """
  
   df = pd.read_sql(query, mydb)


   if df.empty:
       st.warning("No order data found!")
       return


   st.subheader("Order Status Distribution")
   fig, ax = plt.subplots(figsize=(8, 5))
   sns.barplot(x=df["status"], y=df["count"], ax=ax, palette="Blues")


   ax.set_xlabel("Order Status")
   ax.set_ylabel("Number of Orders")
   ax.set_title("Orders by Status")
   ax.bar_label(ax.containers[0])  # Show values on bars
   st.pyplot(fig)  # Display in Streamlit


def get_monthly_profit():
   query = """
       SELECT o.order_date, o.quantity, o.final_price, p.cost_price
       FROM Orders o
       JOIN Product p ON o.product_id = p.product_id
       WHERE o.status = 'Completed'
   """
  
   df = pd.read_sql(query, mydb)


   if df.empty:
       st.warning("No completed orders found!")
       return None


   df['order_date'] = pd.to_datetime(df['order_date'])
   df['year_month'] = df['order_date'].dt.strftime('%Y-%m')
   df['profit'] = (df['final_price'] - df['cost_price']) * df['quantity']
   profit_df = df.groupby('year_month', as_index=False)['profit'].sum()


   return profit_df


def get_monthly_profit1(year):
   query = """
       SELECT o.order_date, o.quantity, o.final_price, p.cost_price
       FROM Orders o
       JOIN Product p ON o.product_id = p.product_id
       WHERE o.status = 'Completed'
   """
  
   df = pd.read_sql(query, mydb)


   if df.empty:
       st.warning("No completed orders found!")
       return None
  
   df['order_date'] = pd.to_datetime(df['order_date'])
   df['year'] = df['order_date'].dt.year
   df['month'] = df['order_date'].dt.month
   year = int(year)  # Convert input year to integer
   df = df[df["year"] == year]
   df['year_month'] = df['order_date'].dt.strftime('%Y-%m')
   df['profit'] = (df['final_price'] - df['cost_price']) * df['quantity']
   profit_df = df.groupby('year_month', as_index=False)['profit'].sum()


   return profit_df


def plot_monthly_profit():
   df = get_monthly_profit()
   if df is None:
       return
   df["year_month"] = pd.to_datetime(df["year_month"], format="%Y-%m")


   st.subheader("Monthly Profit Trend")
   fig, ax = plt.subplots(figsize=(10, 5))
   sns.lineplot(x=df["year_month"], y=df["profit"], marker="o", ax=ax, color="g")


   ax.set_xlabel("Year-Month")
   ax.set_ylabel("Total Profit")
   ax.set_title("Monthly Profit Trend")
   ax.grid(True, linestyle="--", alpha=0.7)
   plt.xticks(rotation=45)
   st.pyplot(fig)


def plot_monthly_profit1(year):
   df = get_monthly_profit1(year)
   if df is None:
       return
   df["year_month"] = pd.to_datetime(df["year_month"], format="%Y-%m")


   st.subheader("Monthly Profit Trend "+ year)
   fig, ax = plt.subplots(figsize=(10, 5))
   sns.lineplot(x=df["year_month"], y=df["profit"], marker="o", ax=ax, color="g")


   ax.set_xlabel("Year-Month")
   ax.set_ylabel("Total Profit")
   ax.set_title("Monthly Profit Trend "+year)
   ax.grid(True, linestyle="--", alpha=0.7)
   plt.xticks(rotation=45)
   st.pyplot(fig)


def create_ticket(title, description, customer_id, user_id):
   query = """INSERT INTO Tickets (title, description, customer_id, user_id)
              VALUES (%s, %s, %s, %s)"""
   cursor.execute(query, (title, description, customer_id, user_id))
   mydb.commit()
   st.success("Ticket created successfully!")




def update_ticket_status(ticket_id, new_status):
   query = """UPDATE Tickets SET status = %s WHERE ticket_id = %s"""
   cursor.execute(query, (new_status, ticket_id))
   mydb.commit()
   st.success("Ticket status updated successfully!")




def delete_ticket(ticket_id):
   query = """DELETE FROM Tickets WHERE ticket_id = %s"""
   cursor.execute(query, (ticket_id,))
   mydb.commit()
   st.success("Ticket deleted successfully!")




def view_all_tickets():
   query = "SELECT * FROM Tickets"
   df = pd.read_sql(query, mydb)
   st.dataframe(df)


def view_my_tickets(user_id):
   query = """SELECT * FROM Tickets WHERE user_id = %s"""
   df = pd.read_sql(query, mydb, params=(user_id,))
   st.dataframe(df)


def fetch_data(query):
   df = pd.read_sql(query, mydb)
   return df


def key_metrics():
   st.title("Key Metrics")


   col1, col2, col3 = st.columns(3)
   total_customers = fetch_data("SELECT COUNT(*) as count FROM Customer")["count"].iloc[0]
   total_orders = fetch_data("SELECT COUNT(*) as count FROM Orders")["count"].iloc[0]
   total_sales = fetch_data("SELECT SUM(total_amount) as sales FROM Orders WHERE status='Completed'")["sales"].iloc[0]


   col1.metric("Total Customers", total_customers)
   col2.metric("Total Orders", total_orders)
   col3.metric("Total Sales Revenue ($)", total_sales)


   order_status_df = fetch_data("SELECT status, COUNT(*) as count FROM Orders GROUP BY status")
   fig, ax = plt.subplots()
   sns.barplot(x=order_status_df["status"], y=order_status_df["count"], ax=ax, palette="coolwarm")
   ax.set_title("Orders by Status")
   st.pyplot(fig)


   plot_sales_by_year("2025")


st.title("CUSTOMER MANAGEMENT SYSTEM")
if 'logged_in' not in st.session_state:
   st.session_state['logged_in'] = False




if not st.session_state['logged_in']:
   choice = st.sidebar.selectbox("My Menu", ("Home", "Sales", "Support", "Manager", "Admin"))
   if choice == "Home":
       st.image("/Users/sumanauppala/Downloads/1a.jpg")
   elif choice == "Sales" or choice == "Support" or choice == "Manager" or choice == "Admin":
       login()


if st.session_state['logged_in'] and st.session_state['logged_in'] is True:
   st.sidebar.empty()
   col1, col2 = st.columns([1, 1])
   with col1:
       if st.button("Home", key="home_button"):
           st.image("/Users/sumanauppala/Downloads/1a.jpg")
   with col2:
       if st.button("Logout", key="logout_button"):
           logout()




   role = st.session_state.get('role', None)
  
   if role == "Admin":
       st.subheader("Admin Dashboard")
       admin_main_options = st.selectbox("Main Menu", ("", "Product Dashboard", "User Dashboard"))
       if admin_main_options == "Product Dashboard":
           admin_options = st.selectbox("Admin Options", ("", "Create New Product", "Update Stock", "Delete Product", "View Products"))
           if admin_options == "Create New Product":
               st.subheader("Add Product")
               product_name = st.text_input("Product Name")
               description = st.text_area("Description")
               cost_price = st.number_input("Cost Price", min_value=0.01, format="%.2f")
               selling_price = st.number_input("Selling Price", min_value=0.01, format="%.2f")
               stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
               create_btn = st.button("Create Product")
               if create_btn:
                   create_product(product_name, description, cost_price, selling_price, stock_quantity)


           if admin_options == "Update Stock":
               st.subheader("Update Product Stock")
               product_id = st.number_input("Product ID", min_value=1, step=1)
               new_stock = st.number_input("New Stock Quantity", min_value=0, step=1)
               update_stock_btn = st.button("Update Stock")
               if update_stock_btn:
                   update_stock_quantity(product_id, new_stock)


           if admin_options == "Delete Product":
               st.subheader("Delete Product")
               delete_product_id = st.number_input("Product ID", min_value=1, step=1)
               delete_btn = st.button("Delete Product")
               if delete_btn:
                   delete_product(delete_product_id)


           if admin_options == "View Products":
               view_products()


       if admin_main_options == "User Dashboard":
           admin_options = st.selectbox("Admin Options", ("", "Create User", "View Users", "Delete User"))
           if admin_options == "Create User":
               st.subheader("Add New User")
               name = st.text_input("Name")
               email = st.text_input("Email")
               username = st.text_input("Username")
               password_ = st.text_input("Password", type="password")
               address = st.text_area("Address")
               phone_number = st.text_input("Phone Number")
               role = st.selectbox("Role", ["Sales", "Support", "Manager"])
               create_btn = st.button("Create User")
               if create_btn:
                   create_user(name, email, username, password_, address, phone_number, role)


           if admin_options == "View Users":
               st.subheader("View Users")
               view_users()


           if admin_options == "Delete User":
               st.subheader("Delete User")
               delete_user_id = st.number_input("User ID", min_value=1, step=1)
               delete_btn = st.button("Delete User")


               if delete_btn:
                   delete_user(delete_user_id)
          
   if role == "Sales" or role == "Manager" or role=="Admin":
       st.subheader("Sales Dashboard")
       menu_list = ()
       if role == "Sales":
           menu_list = ("", "Customer Dashboard", "Leads Dashboard", "Follow up Dashboard", "Orders Dashboard")
       elif role == "Manager" or role == "Admin":
           menu_list = ("", "Customer Dashboard", "Leads Dashboard", "Follow up Dashboard", "Orders Dashboard", "Sales Analysis")
       sales_main_options = st.selectbox("Main Menu", menu_list)
       if sales_main_options == "Customer Dashboard":
           sales_choice = st.selectbox("Sales Options", ("", "Add Customer", "Edit Customer POC", "Delete Customer", "View Customers"))
           if sales_choice == "Add Customer":
               st.subheader("Add Customer")
               name = st.text_input("Customer Name")
               email_id = st.text_input("Email ID")
               contact = st.text_input("Contact")
               poc = st.text_input("Point of Contact (POC)")
               poc_email = st.text_input("POC Email")
               address = st.text_area("Address")
               website = st.text_input("Website")
               if st.button("Submit"):
                   add_customer(name, email_id, contact, poc, poc_email, address, website)


           if sales_choice == "View Customers":
               st.subheader("Customers ")
               customers = get_all_customers()
               if customers:
                   df = pd.DataFrame(customers)
                   st.dataframe(df)
               else:
                   st.warning("No customers found.")


           if sales_choice == "Delete Customer":
               st.subheader("Delete Customer")
               customer_id = st.number_input("Enter Customer ID to Delete", min_value=1, step=1)
               if st.button("Delete"):
                   delete_customer(customer_id)


           if sales_choice == "Edit Customer POC":
               st.subheader("Edit Customer POC")
               customer_id = st.number_input("Customer ID", min_value=1, step=1)
               new_poc = st.text_input("New POC Name")
               new_poc_email = st.text_input("New POC Email")


               if st.button("Update POC"):
                   edit_customer_poc(customer_id, new_poc, new_poc_email)


       if sales_main_options == "Leads Dashboard":
           sales_choice = st.selectbox("Sales Options", ("", "Add Lead", "Update Lead Status", "Update Lead POC", "Update Lead Notes", "View Leads"))
           if sales_choice == "Add Lead":
               st.subheader("Add New Lead")
               name = st.text_input("Lead Name")
               email_id = st.text_input("Email ID")
               contact = st.text_input("Contact")
               poc = st.text_input("Point of Contact (POC)")
               poc_email = st.text_input("POC Email")
               address = st.text_area("Address")
               status = st.selectbox("Status", ["new", "inprogress", "converted", "lost"])
               lead_source = st.text_input("Lead Source")
               last_follow_up_date = st.date_input("Last Follow-up Date")
               notes = st.text_area("Notes")


               if st.button("Submit"):
                   add_lead(name, email_id, contact, poc, poc_email, address, status, lead_source, last_follow_up_date, notes)


           if sales_choice == "Update Lead Status":
               st.subheader("Update Lead Status")
               lead_id = st.number_input("Lead ID", min_value=1, step=1)
               new_status = st.selectbox("New Status", ["new", "inprogress", "converted", "lost"])
               if st.button("Update Status"):
                   update_lead_status(lead_id, new_status)


           if sales_choice == "Update Lead POC":
               st.subheader("Update Lead POC")
               lead_id = st.number_input("Lead ID", min_value=1, step=1)
               new_poc = st.text_input("New POC Name")
               new_poc_email = st.text_input("New POC Email")
               if st.button("Update POC"):
                   update_lead_poc(lead_id, new_poc, new_poc_email)


           if sales_choice == "Update Lead Notes":
               st.subheader("Update Lead Notes")
               lead_id = st.number_input("Lead ID", min_value=1, step=1)
               new_notes = st.text_area("New Notes")
               if st.button("Update Notes"):
                   update_lead_notes(lead_id, new_notes)


           if sales_choice == "View Leads":
               st.subheader("Leads ")
               leads_data = fetch_leads()
               if leads_data:
                   df = pd.DataFrame(leads_data)
                   df = df.rename(columns={
                       "lead_id": "Lead ID",
                       "name": "Name",
                       "email_id": "Email",
                       "contact": "Contact",
                       "poc": "POC",
                       "poc_email": "POC Email",
                       "address": "Address",
                       "status": "Status",
                       "lead_source": "Lead Source",
                       "last_follow_up_date": "Last Follow-Up",
                       "notes": "Notes",
                       "created_at": "Created At"
                   })
                   st.dataframe(df)
               else:
                   st.warning("No leads found!")


          
       if sales_main_options == "Follow up Dashboard":
           sales_choice = st.selectbox("Sales Options", ("", "Schedule Follow-up", "Update Follow-up status", "Update Follow-up Assignee", "View Follow-ups by entity", "View My Follow ups"))
           if sales_choice == "Schedule Follow-up":
               st.subheader("Schedule Follow-Up")
               status = st.selectbox("Status", ["new", "inprogress", "completed"])
               meetlink = st.text_input("Meeting Link (Optional)")
               followup_time = st.date_input("Follow-up Date")
               assignee = st.session_state['user_id']
               entity_type = st.selectbox("Entity Type", ["lead", "customer"])
               entity_id = st.number_input("Entity ID", min_value=1, step=1)
               comments = st.text_area("Comments")
               submit_button = st.button("Schedule Follow-Up")


               if submit_button:
                   schedule_followup(status, meetlink, followup_time, assignee, entity_type, entity_id, comments)


           if sales_choice == "Update Follow-up status":
               st.subheader("Update Follow-Up Status")
               followup_id = st.number_input("Follow-Up ID", min_value=1, step=1)
               new_status = st.selectbox("New Status", ["new", "inprogress", "completed"])
               new_comments = st.text_area("Add Comments")
               current_user = st.session_state['user_id']
               update_status_btn = st.button("Update Status")
               if update_status_btn:
                   update_followup_status_and_comments(followup_id, new_status, new_comments, current_user)


           if sales_choice == "Update Follow-up Assignee":
               followup_id_assignee = st.number_input("Follow-Up ID (Assignee Update)", min_value=1, step=1)
               new_assignee = st.text_input("New Assignee (User ID)")
               update_assignee_btn = st.button("Update Assignee")
               if update_assignee_btn:
                   update_followup_assignee(followup_id_assignee, new_assignee)


           if sales_choice == "View Follow-ups by entity":
               st.subheader("View Follow-Ups by Entity")
               entity_type_view = st.selectbox("Select Entity Type", ["lead", "customer"])
               entity_id_view = st.number_input("Enter Entity ID", min_value=1, step=1)
               view_entity_btn = st.button("View Follow-Ups")
               if view_entity_btn:
                   entity_followups = get_followups_by_entity(entity_type_view, entity_id_view)
                   if entity_followups:
                       df = pd.DataFrame(entity_followups)
                       df.columns = [
                           "Follow-Up ID", "Status", "Meet Link", "Follow-Up Time",
                           "Assignee", "Entity Type", "Entity ID", "Comments", "Created At"
                       ]
                       st.dataframe(df)
                   else:
                       st.warning("No follow-ups found for this entity.")


           if sales_choice == "View My Follow ups":
               st.subheader("Follow ups list")
               assignee_view = st.session_state['user_id']
               view_assignee_btn = st.button("View Follow-Ups")
               if view_assignee_btn:
                   assignee_followups = get_followups_by_assignee(assignee_view)
                   if assignee_followups:
                       df = pd.DataFrame(assignee_followups)
                       df.columns = [
                           "Follow-Up ID", "Status", "Meet Link", "Follow-Up Time",
                           "Assignee", "Entity Type", "Entity ID", "Comments", "Created At"
                       ]
                       st.dataframe(df)
                   else:
                       st.warning("No follow-ups found for this assignee.")


       if sales_main_options == "Orders Dashboard":
           sales_choice = st.selectbox("Sales Options", ("", "Products", "Create Order", "Update Order Status", "Update Payment Status", "Update Delivery date", "Update Review", "View Orders"))
           if sales_choice == "Products":
               view_products()


           if sales_choice == "Create Order":
               st.subheader("Create New Order")
               product_id = st.number_input("Product ID", min_value=1, step=1)
               customer_name = st.selectbox("Select Customers", get_all_customers())
               user_id = st.session_state['user_id']
               quantity = st.number_input("Quantity", min_value=1, step=1)
               final_price = st.number_input("Final Price", min_value=0.01, format="%.2f")
               delivery_date = st.date_input("Delivery Date")
               create_btn = st.button("Create Order")
               if create_btn:
                   customer_id = customer_name[0]
                   if customer_id:
                       create_order(product_id, customer_id, user_id, quantity, quantity*final_price, final_price, delivery_date)
                   else:
                       st.error("Customer not found!")


           if sales_choice == "Update Order Status":
               st.subheader("Update Order Status")
               order_id = st.number_input("Order ID", min_value=1, step=1)
               new_status = st.selectbox("New Status", ["Pending", "Completed", "Cancelled"])
               update_status_btn = st.button("Update Status")


               if update_status_btn:
                   update_order_status(order_id, new_status)


           if sales_choice == "Update Payment Status":
               st.subheader("Update Payment Status")
               order_id = st.number_input("Order ID", min_value=1, step=1)
               new_payment_status = st.selectbox("Payment Status", ["Pending", "Paid", "Overdue"])
               update_payment_btn = st.button("Update Payment Status")


               if update_payment_btn:
                   update_payment_status(order_id, new_payment_status)


           if sales_choice == "Update Delivery date":
               st.subheader("Update Delivery date")
               order_id = st.number_input("Order ID", min_value=1, step=1)
               new_delivery_date = st.date_input("New Delivery Date")
               update_delivery_btn = st.button("Update Delivery Date")


               if update_delivery_btn:
                   update_delivery_date(order_id, new_delivery_date)


           if sales_choice == "Update Review":
               st.subheader("Update Order Review")
               order_id = st.number_input("Order ID", min_value=1, step=1)
               review = st.slider("Review (1 to 5)", 1, 5)
               update_review_btn = st.button("Update Review")


               if update_review_btn:
                   update_review(order_id, review)


           if sales_choice == "View Orders":
               view_option = st.selectbox("View Orders By", ["", "Customer Name", "User ID", "Product ID"])
               view_id = 0
               customer_name = ()
               if view_option == "Customer Name":
                   customer_name = st.selectbox("Select Customers", get_all_customers())
               elif view_option == "":
                   pass
               else:
                   view_id = st.number_input("Enter ID", min_value=1, step=1)
               view_orders_btn = st.button("View Orders")
               if view_orders_btn:
                   if view_option == "":
                       view_orders()
                   if view_option == "Customer Name":
                       view_id = customer_name[0]
                   if view_id:
                       if view_option == "Customer Name":
                           view_orders_by("customer_id", view_id)
                       elif view_option == "User ID":
                           view_orders_by("user_id", view_id)
                       elif view_option == "Product ID":
                           view_orders_by("product_id", view_id)


       if sales_main_options == "Sales Analysis":
           sales_choice =  st.selectbox("Sales Options", ["Key Metrics", "Sales by Product ID", "Quantity by Product ID","Profit by Product ID", "Payment status", "Order Status", "Sales by order date", "Yearly & Monthly sales", "Yearly & Monthly Profit"])
           if sales_choice == "Key Metrics":
               key_metrics()
           if sales_choice == "Sales by Product ID":
               plot_sales_by_product()
           if sales_choice == "Quantity by Product ID":
               plot_sales_by_product_quantity()
           if sales_choice == "Profit by Product ID":
               plot_profit_by_product()
           if sales_choice == "Payment status":
               plot_payment_status()
           if sales_choice == "Sales by order date":
               plot_sales_by_time()
           if sales_choice == "Order Status":
               plot_order_status_count()
           if sales_choice == "Yearly & Monthly sales":
               year = st.selectbox("Select Customers", ["To date", "2023", "2024", "2025"])
               view_sales = st.button("View Yearly Sales")
               if view_sales:
                   if year == "To date":
                       plot_sales_by_year1()
                   else:
                       plot_sales_by_year(year)


           if sales_choice == "Yearly & Monthly Profit":
               year = st.selectbox("Select Customers", ["To date", "2023", "2024", "2025"])
               view_profits = st.button("View Yearly Profits")
               if view_profits:
                   if year == "To date":
                       plot_monthly_profit()
                   else:
                       plot_monthly_profit1(year)


   if role == "Support" or role=="Admin":
       st.subheader("Support Dashboard")
       support_main_menu = st.selectbox("Support Options", ["", "Create Ticket", "Update Ticket Status", "Delete Ticket", "View My Tickets", "View All Tickets"])
       if support_main_menu == "Create Ticket":
           st.subheader("Create a New Ticket")
           title = st.text_input("Title")
           description = st.text_area("Description")
           customer_id = st.number_input("Customer ID", min_value=1, step=1)
           user_id = st.session_state['user_id']
           if st.button("Create Ticket"):
               create_ticket(title, description, customer_id, user_id)


       elif support_main_menu == "Update Ticket Status":
           st.subheader("Update Ticket Status")
           ticket_id = st.number_input("Ticket ID", min_value=1, step=1)
           new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved", "Closed"])
           if st.button("Update Status"):
               update_ticket_status(ticket_id, new_status)


       elif support_main_menu == "Delete Ticket":
           st.subheader("Delete a Ticket")
           ticket_id = st.number_input("Ticket ID", min_value=1, step=1)
           if st.button("Delete Ticket"):
               delete_ticket(ticket_id)


       elif support_main_menu == "View My Tickets":
           st.subheader("View My Tickets")
           user_id = st.session_state['user_id']
           if st.button("View"):
               view_my_tickets(user_id)


       elif support_main_menu == "View All Tickets":
           st.subheader("All Tickets (Admin)")
           if st.button("View All Tickets"):
               view_all_tickets()
