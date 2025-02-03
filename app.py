import os
import flask
import vanna
from vanna.remote import VannaDefault
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

load_dotenv()

api_key = os.getenv('VANNA_API_KEY')
vanna_model_name = os.getenv('VANNA_MODEL')

app = Flask(__name__)

vn = VannaDefault(
    model=vanna_model_name,
    api_key=api_key
)

vn.connect_to_postgres(host=os.getenv('DB_HOST'), dbname=os.getenv('DB_NAME'), user='postgres', password=os.getenv('DB_PASSWORD'), port=5432)

# df_tables = vn.run_sql("""
# SELECT
#     table_catalog,
#     table_schema,
#     table_name
# FROM INFORMATION_SCHEMA.TABLES
# WHERE table_type = 'BASE TABLE'
#   AND table_schema NOT IN ('pg_catalog', 'information_schema');
# """)

# for index, row in df_tables.iterrows():
#     doc_line = f"Database: {row['table_catalog']} / Schema: {row['table_schema']} / Table: {row['table_name']}"
#     vn.train(documentation=doc_line)

# df_fk = vn.run_sql("""
# SELECT
#   tc.table_catalog,               -- add table_catalog here, too!
#   tc.table_schema,
#   tc.table_name,
#   kcu.column_name,
#   ccu.table_schema AS foreign_table_schema,
#   ccu.table_name AS foreign_table_name,
#   ccu.column_name AS foreign_column_name
# FROM information_schema.table_constraints AS tc
# JOIN information_schema.key_column_usage AS kcu
#   ON tc.constraint_name = kcu.constraint_name
#   AND tc.table_schema = kcu.table_schema
# JOIN information_schema.constraint_column_usage AS ccu
#   ON ccu.constraint_name = tc.constraint_name
#   AND ccu.table_schema = tc.table_schema
# WHERE tc.constraint_type = 'FOREIGN KEY'
#   AND tc.table_schema NOT IN ('pg_catalog', 'information_schema');
# """)

# for index, row in df_fk.iterrows():
#     doc_line = f"Database: {row['table_catalog']} / Schema: {row['table_schema']} / Table: {row['table_name']}"
#     vn.train(documentation=doc_line)

# vn.train(documentation="All the Captains, Agents, and Organization related people are in User table with different userTypes, and UserType is another Table which specify type of user. and Customers table consists of registered users, passengers table consists of passenegers who travelled with us and need not to be in customers.")
# vn.train(documentation="The User table has all the information about the users, and the UserType table has the type of users. The Customers table has the information about the registered users, and the Passengers table has the information about the passengers who have traveled with us.")
# vn.train(documentation="ReservedTickets table consists of all booked tickets and trip details, passenger details")
# vn.train(documentation="TicketTransaction table consists of all the transactions related to tickets, and this table has all the payment details with necessary columns of what platform and when it got booked")
# vn.train(documentation="ReservedTicketSeats table consists of and triplevel details, seatIds, passenger details of seat and so on")
# vn.train(documentation="AgentPaymentTransaction table consists of all the transactions related to agents, and this table has all the payment details with necessary columns of what platform and when it got booked")

# vn.train(sql='''
#           select rt."invoiceNumber" as pnr,
#           DATE(pgt."createdAt") as transactionDate,
#           tt."collectAmount" as transactionCollectAmount,
#           pgt."orderId" as txnid
#           from "TicketTransactions" tt 
#           join "ReservedTickets" rt 
#           on tt."ticketId" = rt.id
#           left join "PaymentGatewayTransactions" pgt 
#           on tt."paymentId" = pgt.id
#           where tt."paymentId" is not null 
#           and rt."subCategory" in ('Android','Website','IOS','Captain','QR')
#           and DATE(pgt."createdAt") between '2024-12-26' and '2025-01-20'
#            ''')

# vn.train(sql='''
#            select count(*) from (select u.mobile,u."firstName",u."lastName", apt.amount as "amount", apt."createdAt",
# 'Recharge' as "comment", pgt."orderId"
# from "AgentPaymentTransactions" apt 
# join "User" u on apt."uuid" = u.id 
# left join "PaymentGatewayTransactions" pgt on cast(apt."amount" as INTEGER) = cast(pgt."amount" as INTEGER) 
# --and date(apt."createdAt") = DATE(pgt."createdAt")
# and DATE_TRUNC('hour', apt."createdAt") = DATE_TRUNC('hour', pgt."createdAt")
# --and DATE_TRUNC('minute', apt."createdAt") = DATE_TRUNC('minute', pgt."createdAt")
# where DATE(apt."createdAt") BETWEEN '2024-11-07' and '2025-01-20'
# and (pgt."orderId" like 'r_%' or pgt."orderId" like 'freshbuspvtltd-r_%')
# and pgt.status = 'CHARGED') as count
#            ''')

# vn.train(sql='''
#             select u.mobile,u."firstName",u."lastName",
#             tt."financialTransactionType", rt."invoiceNumber", tt.amount, tt.discount, tt.tax, tt."collectAmount", 
#             tt."commission" as "commission", tt."financialTransactionType" as "commissionType",
#             tt."createdAt", 'Ticket Transaction' as "comment", '' as "orderId"
#             from "TicketTransactions" tt 
#             join "User" u on tt."createdById" = u.id 
#             join "ReservedTickets" rt on tt."ticketId" = rt.id
#             where tt."createdById" not in (1684,1319,1320,8)  and DATE(tt."createdAt") BETWEEN '2024-11-07' and '2025-01-20'
#             and u."userTypeId" in (6, 2)
#             and tt.id = 565565
#            ''')

# vn.train(sql='''
#             SELECT tt."ticketId" AS id, 
#                     rt."invoiceNumber" AS ticket_no, 
#                     c.id as customer_id, 
#                     case when c."name" = '' then p."name" else c."name" end as customer_name, 
#                     p."name" as passenger_name, 
#                     c.mobile as mobile, 
#                     to_char(t."journeyDate", 'DD-MM-YYYY') AS journey_date, 
#                     to_char(date(tt."createdAt"), 'DD-MM-YYYY') as document_date,
#                     CAST(ROUND(rts."amount" :: NUMERIC, 2) AS INTEGER) as seat_fare, 
#                     CAST(ROUND(rts."tax" :: NUMERIC, 2) AS INTEGER) as seat_tax, 
#                     rts."amount" + rts."tax" AS seat_fare_with_tax,
#                     CAST(rts."discount" AS INTEGER) as seat_discount,
#                     CAST(ROUND(tt."amount" :: NUMERIC, 2) AS INTEGER) AS base_fare, 
#                     cast(ROUND(tt."tax"::NUMERIC, 0)as INTEGER) AS stax_amount, 
#                     CAST(ROUND(tt."discount" :: NUMERIC, 2) AS INTEGER) AS discount, 
#                     CAST(ROUND(tt."amount" + tt."tax", 2) AS INTEGER) as collect_amount,
#                     CAST(tt."collectAmount" AS INTEGER) as c_amount, 
#                     CAST((tt."tax" / tt."amount") * 100 AS INTEGER) as tax_rate,
#                     case when u."firstName" is null then 'Online' else u."firstName" end as booked_byname, 
#                     rt."subCategory" AS Booked_By_Name, 
#                     bp."name" AS Boarding_Place_Name, 
#                     dp."name" AS Dropping_Place_Name,
#                     gct."coins" as green_coins,
#                     case 
#                     	when rts.pass = true then 1
#                     	else 0
#                     end as freshpass_status,
#                     case when pgt.response :: jsonb ->> 'PG_TYPE' = 'UPI-PG' then 'upi' when pgt.response :: jsonb ->> 'PG_TYPE' = 'CC-PG' then 'card' when pgt.response :: jsonb ->> 'PG_TYPE' = 'DC-PG' then 'card' else 'upi' end as payment_type, 
#                     sc2."seat_numbers", 
#                     sc."seat_count" ,
#                     s2."id" as sourceid,
#                     s3."id" as desinationid,
#                     rts.pass
#                     FROM 
#                     "TicketTransactions" tt 
#                     JOIN "ReservedTickets" rt ON rt."id" = tt."ticketId" 
#                     JOIN "ReservedTicketSeats" rts ON rts."ticketId" = rt."id" 
#                     JOIN "Trips" t ON t.id = rt."tripId" 
#                     JOIN "Services" s ON s.id = t."serviceId" 
#                     JOIN "Stations" s2 ON s2.id = s."sourceId" 
#                     JOIN "Stations" s3 ON s3.id = s."destinationId" 
#                     JOIN "Passengers" p ON p.id = rts."passengerId" 
#                     JOIN "Customers" c ON c.id = p."customerId" 
#                     left JOIN "User" u ON tt."createdById" = u.id 
#                     LEFT JOIN "UserAgentDetails" uad ON uad."uuid" = u.id 
#                     LEFT JOIN "User" u2 ON uad."distributorId" = u2.id 
#                     JOIN "BoardingPoints" bp ON rt."boardingPointId" = bp.id 
#                     JOIN "DroppingPoints" dp ON rt."droppingPointId" = dp.id 
#                     LEFT JOIN "PaymentGatewayTransactions" pgt ON tt."paymentId" = pgt.id
#                     left join "GreenCoinTransactions" gct on tt."greenCoinsTransactionId" = gct.id
#                     left join (
#                         select 
#                         "ticketId",
#                         count(1) as seat_count 
#                         from 
#                         "ReservedTicketSeats" 
#                         group by 
#                         "ticketId"
#                     ) as sc on rt.id = sc."ticketId" 
#                     left join (
#                         SELECT 
#                         "ticketId", 
#                         ARRAY_AGG("seatId") AS seat_numbers
#                         FROM 
#                         "ReservedTicketSeats" 
#                         GROUP BY 
#                         "ticketId"
#                     ) as sc2 on rt.id = sc2."ticketId" 
#                     where rts."active" = true 
#                     and rt."mainCategory" IN ('Online','Offline')
#                     and tt."transactionType" = 'Booked'
#                     and rt."invoiceNumber" in ('FRE532004')
           
#            ''')

# vn.train(sql='''
#          SELECT count(ts."seatId") as seatcount,t.id,t."serviceId" 
# FROM "Trips" t
# JOIN "TripSeats" ts ON t.id = ts."tripId"
# JOIN "TripBoardingPoints" tbp on t.id = tbp."tripId" 
# WHERE t.id in (select id from "Trips" t where t."serviceId" in (55,47,61,48,37,38,119,99,58,59,50,51,57,43,44,52,36,29,22,9,31,103,33,54,3,102,34,90,21,89,7,13,97) and t."journeyDate" = '2025-02-17')
#   AND ts.available = FALSE
#   AND ts."availableAt" = tbp."currentTime"
#   group by t.id
#   order by seatcount asc
#          ''')

# vn.train(sql='''
#           SELECT * 
# FROM "TripBoardingPoints"
# WHERE "boardingPointId" = 29 AND "tripId" IN (
#     SELECT t.id
#     FROM "Trips" t
#     WHERE t."serviceId" = 35 AND t."journeyDate" >= current_date
# );
#          ''')

# vn.train(sql='''
#          SELECT * 
# FROM "Trips" t 
# WHERE "journeyDate" > CURRENT_DATE
#   AND EXTRACT(DOW FROM "journeyDate") = 6 and "serviceId" = 49;
#          ''')

# vn.train(sql='''
#          select count(ts."seatId"),"tripId" from "TripSeats" ts
# join "Trips" t on t.id = ts."tripId" 
# where t."serviceId" in (61,48,38) 
# and "seatId" in (41,42,43,44,45) 
# and available = true
# and "availableAt" is null 
# and (t."journeyDate" >= '2025-01-06' and t."journeyDate" <='2025-01-14')
# group by "tripId" 
#          ''')

# vn.train(sql='''
#          select bp."name",sbp."serviceId",sbp."day",sbp."scheduledTime" from "BoardingPoints" bp 
# join "ServiceBoardingPoints" sbp on bp.id = sbp."boardingPointId"
# where sbp."serviceId" =8
#          ''')

# vn.train(sql='''select rt."subCategory",rt."mainCategory",rt.id,rts.* from "TicketTransactions" tt 
# join "ReservedTickets" rt on tt."ticketId" = rt.id 
# join "RescheduleTicketSeats" rts on rts."ticketId" = tt."ticketId" 
# where tt."freshPassTransactionsId" is not null 
# and tt."financialTransactionType" = 'Credit'
# and rt."mainCategory" is not null 
# and rt."subCategory" = 'Android' 
# group by rts."ticketId" , rt."subCategory" ,rt."mainCategory" ,rt.id,rts.id 
#          ''')

# vn.train(sql='''select * from "ReservedTickets" where "tripId" in (select id from "Trips" where "journeyDate">'2024-12-01' and "journeyDate"<'2025-01-01') '''
# )

@app.route("/")
def home():
    """
    Renders the index.html page from the templates folder.
    """
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    """
    Expects JSON with "question". We'll call vn.ask(...) with run_sql=True,
    returning a JSON response that includes answer, sql, and optional dataframe.
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in JSON"}), 400

    question = data["question"]
    try:
        # ask the LLM to generate & run SQL
        response = vn.ask(question=question, run_sql=True)
        
        df_json = None
        if "df" in response and response["df"] is not None:
            df_json = response["df"].to_dict(orient="records")

        return jsonify({
            "answer": response.get("answer"),
            "sql": response.get("sql"),
            "rows": df_json
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Start the Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)

