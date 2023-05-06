import streamlit as st
import pandas as pd
import sqlite3
import datetime
from datetime import date, timedelta
from pymongo.mongo_client import MongoClient

try:
    conn = sqlite3.connect('HostelApp.db')
    c = conn.cursor()
except sqlite3.Error as e:
    print(e)

uri = "mongodb+srv://ikthor:Earl14ItR4mKnvlf@cluster0.zxomsvv.mongodb.net/?retryWrites=true&w=majority"
mongo_client = MongoClient(uri)
mongo_db = mongo_client['HostelApp']
hostel_app = mongo_db['hostels_info']
room_app = mongo_db['rooms_info']
passport_app = mongo_db['passports']

# room_app.insert_many([
#     {"_id": 1, "beds": 1, "number": 101, "floor": 1},
#     {"_id": 2, "beds": 2, "number": 102, "floor": 1},
#     {"_id": 3, "beds": 3, "number": 201, "floor": 2},
#     {"_id": 4, "beds": 2, "number": 202, "floor": 2},
#     {"_id": 5, "beds": 1, "number": 101, "floor": 1},
#     {"_id": 6, "beds": 2, "number": 102, "floor": 1},
#     {"_id": 7, "beds": 3, "number": 201, "floor": 2},
#     {"_id": 8, "beds": 2, "number": 202, "floor": 2},
#     {"_id": 9, "beds": 3, "number": 201, "floor": 2},
#     {"_id": 10, "beds": 4, "number": 301, "floor": 3},
#     {"_id": 11, "beds": 3, "number": 201, "floor": 2},
#     {"_id": 12, "beds": 3, "number": 202, "floor": 2},
#     {"_id": 13, "beds": 1, "number": 201, "floor": 2},
#     {"_id": 14, "beds": 2, "number": 202, "floor": 2},
#     {"_id": 15, "beds": 2, "number": 203, "floor": 2},
#     {"_id": 16, "beds": 3, "number": 204, "floor": 2}
# ])

# hostel_app.insert_many([
#     {"_id": 1, "website": "hotelbeta.ru", "address": "Измайловское ш., 71, корп. 2Б", "phone": "+7 (495) 792-98-98"},
#     {"_id": 2, "website": "izmailovo.ru", "address": "Измайловское ш., 71к4Г-Д", "phone": "+7 (495) 737-70-70"},
#     {"_id": 3, "website": "izmailovo.ru", "address": "Измайловское ш., 71к4Г-Д", "phone": "+7 (495) 737-70-70"},
#     {"_id": 4, "website": "moscowgrandhotel.ru", "address": "Тверская ул., 26/1, корп. 2Б", "phone": "+7 (495) 937-00-00"},
#     {"_id": 5, "website": "hotel-moscow.ru", "address": "Площадь Александра Невского, 2, Санкт-Петербург", "phone": "+7 (812) 333-24-44"}
# ])

db_hostel_types = c.execute("SELECT * FROM Hostel_type").fetchall()
db_countries = c.execute("SELECT * FROM Country").fetchall()
db_room_types = c.execute("SELECT * FROM Room_type").fetchall()
db_book_statuses = c.execute("SELECT * FROM Booking_status").fetchall()
db_works = c.execute("SELECT * FROM Work").fetchall()
db_hostels = c.execute("SELECT * FROM Hostel").fetchall()
db_payment_types = c.execute("SELECT * FROM Payment_type").fetchall()


def main():
    tab1, tab2 = st.tabs(['Вход', 'Регистрация'])
    with tab1:
        st.header('Вход в аккаунт')
        login = st.text_input("Логин")
        password = st.text_input("Пароль", type='password')
        if st.checkbox('Войти'):
            guest_id = c.execute("SELECT guest_id FROM Guest WHERE guest_login = ? AND guest_password = ?",
                                 (login, password,)).fetchone()
            worker = c.execute("SELECT worker_id, worker_role_id FROM Worker "
                               "WHERE worker_login = ? AND worker_password = ?",
                               (login, password,)).fetchone()
            if guest_id:
                guest_menu(guest_id[0])
            elif worker:
                worker_menu(worker)
            else:
                st.error('Вы ввели неправильные логин или пароль')
    with tab2:
        registrate_guest()


def guest_menu(guest_id):
    client_menu_choice = st.selectbox('Выберите меню', ['Отели', 'Бронирование', 'Проживание', 'Оплата'])
    if client_menu_choice == 'Отели':
        hostel_country = st.radio('Страна', [x[1] for x in db_countries])
        for country in db_countries:
            if country[1] == hostel_country:
                country_id = country[0]
        db_cities = c.execute("SELECT * FROM City WHERE country_id = ?", (country_id,)).fetchall()
        hostel_city = st.selectbox('Город', [x[1] for x in db_cities])
        hostel_stars = st.slider('Количество звезд', 3, 5)
        for city in db_cities:
            if city[1] == hostel_city:
                city_id = city[0]
        db_hostels = c.execute("SELECT * FROM Hostel WHERE hostel_city = ? AND hostel_stars = ?",
                               (city_id, hostel_stars,)).fetchall()
        for hostel in db_hostels:
            display_hostel(hostel, guest_id)
    elif client_menu_choice == 'Бронирование':
        db_bookings = c.execute("SELECT * FROM Room_book WHERE guest_id = ?", (guest_id,)).fetchall()
        for booking in db_bookings:
            if booking[5] == 1:
                display_booking(booking)
    elif client_menu_choice == 'Проживание':
        db_bookings = c.execute("SELECT * FROM Room_book WHERE guest_id = ? AND status_id = ?",
                                (guest_id, 3,)).fetchall()
        for booking in db_bookings:
            display_living(booking)
    elif client_menu_choice == 'Оплата':
        payments = c.execute("SELECT * FROM Payment").fetchall()
        for payment in payments:
            invoice = c.execute("SELECT * FROM Invoice WHERE invoice_id = ?", (payment[1],)).fetchone()
            room_book_id = invoice[1]
            room_book = c.execute("SELECT * FROM Room_book WHERE room_book_id = ?", (room_book_id,)).fetchone()
            payment_guest_id = room_book[2]
            guest = c.execute("SELECT * FROM Guest WHERE guest_id = ?", (guest_id,)).fetchone()
            if guest_id == payment_guest_id:
                with st.container():
                    st.markdown(f'Статус: Оплачено')
                    st.markdown(f'Сумма оплаты: {invoice[2]}')
                    st.markdown(f'Способ оплаты: {db_payment_types[payment[3] - 1][1]}')
                    if st.checkbox('Данные гостя'):
                        st.markdown(f'Гость: {guest[1]} {guest[2]}')
                        st.markdown(f'Телефон: {guest[5]}')


def worker_menu(worker):
    worker_id = worker[0]
    worker_role_id = worker[1]
    if worker_role_id == 1:
        hostel_choice = st.selectbox('Отели', [x[1] for x in db_hostels])
        for hostel_ in db_hostels:
            if hostel_[1] == hostel_choice:
                selected_hostel = hostel_
        worker_menu_choice = st.selectbox('', ['Заселение', 'Обслуживание номеров', 'Счета', 'Оплаты'])
        if worker_menu_choice == 'Заселение':
            in_bookings = c.execute("SELECT * FROM Room_book").fetchall()
            for in_booking in in_bookings:
                if in_booking[5] in [1, 2]:
                    room = c.execute("SELECT * from Room WHERE room_id = ?", (in_booking[1],)).fetchone()
                    hostel_id = room[2]
                    hostel = c.execute("SELECT * from Hostel WHERE hostel_id = ?", (hostel_id,)).fetchone()
                    if hostel[0] == selected_hostel[0]:
                        display_in_bookings(in_booking)
        elif worker_menu_choice == 'Обслуживание номеров':
            display_works()
        elif worker_menu_choice == 'Счета':
            invoices = c.execute("SELECT * FROM Invoice").fetchall()
            for invoice in invoices:
                payment = c.execute("SELECT * FROM Payment WHERE invoice_id = ?", (invoice[0],)).fetchone()
                if not payment:
                    room_book_id = invoice[1]
                    room_book = c.execute("SELECT * FROM Room_book WHERE room_book_id = ?", (room_book_id,)).fetchone()
                    guest_id = room_book[2]
                    guest = c.execute("SELECT * FROM Guest WHERE guest_id = ?", (guest_id,)).fetchone()
                    with st.container():
                        st.subheader(f'Гость: {guest[1]} {guest[2]}')
                        st.markdown(f'Статус: Не оплачено')
                        st.markdown(f'Сумма к оплате: {invoice[2]}')
                        payment_choice_key = 'payment_choice' + str(invoice[0])
                        payment_choice = st.radio('Способ оплаты', [x[1] for x in db_payment_types], key=payment_choice_key)
                        for payment_type in db_payment_types:
                            if payment_type[1] == payment_choice:
                                selected_payment_id = payment_type[0]
                        pay_btn_key = 'pay' + str(invoice[0])
                        if st.button('Оплатить', key=pay_btn_key):
                            c.execute("INSERT INTO Payment (invoice_id, payment_date, payment_type) "
                                      "VALUES (?,?,?)", (invoice[0], date.today(), selected_payment_id,))
                            c.execute("UPDATE Room_book SET status_id = ? WHERE room_book_id = ?",
                                      (2, room_book_id,))
                            conn.commit()
                            st.success('Оплата успешно проведена')
                            st._rerun()
        elif worker_menu_choice == 'Оплаты':
            payments = c.execute("SELECT * FROM Payment").fetchall()
            for payment in payments:
                invoice = c.execute("SELECT * FROM Invoice WHERE invoice_id = ?", (payment[1],)).fetchone()
                room_book_id = invoice[1]
                room_book = c.execute("SELECT * FROM Room_book WHERE room_book_id = ?", (room_book_id,)).fetchone()
                guest_id = room_book[2]
                guest = c.execute("SELECT * FROM Guest WHERE guest_id = ?", (guest_id,)).fetchone()
                with st.container():
                    st.markdown(f'Статус: Оплачено')
                    st.markdown(f'Сумма оплаты: {invoice[2]}')
                    st.markdown(f'Способ оплаты: {db_payment_types[payment[3] - 1][1]}')
                    key_un = 'data_guest' + str(invoice[0])
                    if st.checkbox('Данные гостя', key=key_un):
                        st.markdown(f'Гость: {guest[1]} {guest[2]}')
                        st.markdown(f'Телефон: {guest[5]}')
    elif worker_role_id == 2:
        st.header('Работяга')


def display_works():
    works_status_choice = st.selectbox('', ['Ожидает выполнения', 'Выполняются', 'Выполнено'])
    if works_status_choice == 'Ожидает выполнения':
        status_id_choice = 1
    elif works_status_choice == 'Выполняются':
        status_id_choice = 2
    elif works_status_choice == 'Выполнено':
        status_id_choice = 3
    for work in c.execute("SELECT * FROM WorksInRooms WHERE work_status_id = ?",
                          (status_id_choice,)).fetchall():
        room_book_id = work[1]
        booking = c.execute("SELECT * FROM Room_book WHERE room_book_id = ?", (room_book_id,)).fetchone()
        guest_id = booking[2]
        guest = c.execute("SELECT * FROM Guest WHERE guest_id = ?", (guest_id,)).fetchone()
        room = c.execute("SELECT * FROM Room WHERE room_id = ?", (booking[1],)).fetchone()
        work_id = work[2]
        col1, col2 = st.columns(2)
        with col1:
            room_id = booking[1]
            room = c.execute("SELECT * from Room WHERE room_id = ?", (room_id,)).fetchone()
            hostel_id = room[2]
            hostel = c.execute("SELECT * from Hostel WHERE hostel_id = ?", (hostel_id,)).fetchone()
            room_info = room_app.find_one({"_id": room_id})
            st.markdown(f'Отель: {hostel[1]}')
            st.markdown(f'Номер комнаты: {room_info["number"]}')
            st.markdown(f'Этаж: {room_info["floor"]}')
        with col2:
            st.markdown(f'Гость: {guest[1]} {guest[2]}, {guest[5]}')
            st.markdown(f'Дата назначения: {work[5]}')

        cl1, cl2, cl3 = st.columns(3)
        with cl1:
            start_work_key = 'start_work ' + str(work[0])
            if st.button('Выполнять', key=start_work_key, disabled=True if status_id_choice != 1 else False):
                c.execute("UPDATE WorksInRooms SET work_status_id = ? WHERE id = ?", (2, work[0],))
                conn.commit()
                st.experimental_rerun()
        with cl2:
            complete_work_key = 'complete_work ' + str(work[0])
            if st.button('Сделано', key=complete_work_key, disabled=True if status_id_choice != 2 else False):
                c.execute("UPDATE WorksInRooms SET work_status_id = ? WHERE id = ?", (3, work[0],))
                conn.commit()
                st.experimental_rerun()
        with cl3:
            cancel_work_key = 'cancel_work ' + str(work[0])
            if st.button('Отменить', key=cancel_work_key, disabled=True if status_id_choice == 3 else False):
                c.execute("DELETE FROM WorksInRooms WHERE id = ?", (work[0],))
                conn.commit()
                st.experimental_rerun()


def display_in_bookings(booking):
    room_book_id = booking[0]
    room_id = booking[1]
    guest_id = booking[2]
    guest = c.execute("SELECT * FROM Guest WHERE guest_id = ?", (guest_id,)).fetchone()
    room = c.execute("SELECT * FROM Room WHERE room_id = ?", (booking[1],)).fetchone()
    room_info = room_app.find_one({"_id": room_id})
    hostel_id = room[2]
    hostel = c.execute("SELECT * from Hostel WHERE hostel_id = ?", (hostel_id,)).fetchone()
    st.subheader(f'{hostel[1]}')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'Номер комнаты: {room_info["number"]}')
        st.markdown(f'Этаж: {room_info["floor"]}')
        st.markdown(f'Количество кроватей: {room_info["beds"]}')
        st.markdown(f'Стоимость за ночь: {room[3]}')
    with col2:
        st.markdown(f'Статус: {db_book_statuses[booking[5] - 1][1]}')
        st.markdown(f'Гость: {guest[1]} {guest[2]}, {guest[5]}')
        st.markdown(f'Заселение: {booking[3]}')
        st.markdown(f'Выселение: {booking[4]}')
        settle_key = 'settle_room' + str(room_book_id)
    cancel_book_key = 'cancel_book' + str(booking[0])
    if st.button('Отменить бронирование', key=cancel_book_key):
        c.execute("DELETE FROM Room_book WHERE room_book_id = ?", (booking[0],))
        conn.commit()
        st.experimental_rerun()
    invoice_btn_key = 'invoice' + str(room_book_id)
    if st.button('Выставить счет за проживание', key=invoice_btn_key):
        date_1 = list(map(int, booking[3].split('-')))
        date_2 = list(map(int, booking[4].split('-')))
        check_in_date = date(year=date_1[0], month=date_1[1], day=date_1[2])
        eviction_date = date(year=date_2[0], month=date_2[1], day=date_2[2])
        diff = eviction_date - check_in_date
        amount = diff.days * room[3]
        if not c.execute("SELECT * FROM Invoice WHERE room_book_id = ?", (room_book_id,)).fetchone():
            c.execute("INSERT INTO Invoice (room_book_id, invoice_amount) "
                      "VALUES (?,?)", (room_book_id, amount))
            st.info('Счет за проживание выставлен')
            conn.commit()
        else:
            st.error('Счет уже выставлен')
    if st.checkbox('Начать заселение', key=settle_key):
        settle_guest(guest_id, room_book_id)


def display_living(booking):
    col1, col2 = st.columns(2)
    with col1:
        display_room(c.execute("SELECT * from Room WHERE room_id = ?", (booking[1],)).fetchone())
    with col2:
        work_choice = st.selectbox('Выбор работы', [x[1] for x in db_works])
        for work in db_works:
            if work[1] == work_choice:
                work_choice_id = work[0]
        st.markdown(f'Статус: {db_book_statuses[booking[5] - 1][1]}')
        order_work_key = 'order work' + str(booking[0])
        if st.button('Заказать услугу', key=order_work_key):
            if not c.execute("SELECT * FROM WorksInRooms WHERE room_book_id = ? AND work_id = ?",
                             (booking[0], work_choice_id,)).fetchone():
                c.execute("INSERT INTO WorksInRooms (room_book_id, work_id, work_status_id, date) "
                          "VALUES (?,?,?,?)", (booking[0], work_choice_id, 1, date.today(),))
                conn.commit()
                st.experimental_rerun()
            else:
                st.error('Данная услуга уже обрабатывается')
    st.subheader('Заказанные услуги')
    for work in c.execute("SELECT * FROM WorksInRooms WHERE room_book_id = ? AND work_status_id = ?",
                          (booking[0], 1,)).fetchall():
        work_id = work[2]
        work_info = c.execute("SELECT work_name FROM Work WHERE work_id = ?", (work_id,)).fetchone()[0]
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'{work_info}')
                st.markdown(f'Дата назначения: {work[5]}')
            with col2:
                cancel_work_key = 'cancel_work ' + str(work[0])
                if st.button('Отменить работу', key=cancel_work_key):
                    c.execute("DELETE FROM WorksInRooms WHERE id = ?", (work[0],))
                    conn.commit()


def display_booking(booking):
    room = c.execute("SELECT * from Room WHERE room_id = ?", (booking[1],)).fetchone()
    hostel_id = room[2]
    hostel = c.execute("SELECT * from Hostel WHERE hostel_id = ?", (hostel_id,)).fetchone()
    st.subheader(f'{hostel[1]}')
    col1, col2 = st.columns(2)
    with col1:
        display_room(room)
    with col2:
        st.markdown(f'Статус: {db_book_statuses[booking[5] - 1][1]}')
        st.markdown(f'Заселение: {booking[3]}')
        st.markdown(f'Выселение: {booking[4]}')
        cancel_book_key = 'cancel_book' + str(booking[0])
        if st.button('Отменить бронирование', key=cancel_book_key):
            c.execute("DELETE FROM Room_book WHERE room_book_id = ?", (booking[0],))
            conn.commit()
            st.experimental_rerun()


def display_hostel(hostel, guest_id):
    col1, col2 = st.columns(2)
    with col1:
        hostel_info = hostel_app.find_one({"_id": hostel[0]})
        st.subheader(db_hostel_types[hostel[2] - 1][1])
        st.markdown(hostel_info['website'])
        st.markdown(hostel_info['address'])
        st.markdown(hostel_info['phone'])
    with col2:
        st.subheader(hostel[1])
        in_date_key = 'in_date ' + str(hostel[0])
        out_date_key = 'out_date ' + str(hostel[0])
        room_type_key = 'room_type ' + str(hostel[0])
        in_date = st.date_input('Дата въезда', min_value=date.today(), max_value=(date.today() + timedelta(weeks=4)),
                                key=in_date_key)
        out_date = st.date_input('Дата въезда', min_value=(date.today() + timedelta(days=1)),
                                 max_value=(date.today() + timedelta(weeks=4, days=1)), key=out_date_key,
                                 value=(date.today() + timedelta(days=1)))
    room_type_choice = st.selectbox('Тип номера', [x[1] for x in db_room_types], key=room_type_key)
    for room_type in db_room_types:
        if room_type[1] == room_type_choice:
            room_type_id = room_type[0]
    db_hotel_rooms = c.execute("SELECT * FROM Room WHERE hostel_id = ? AND type_id = ?",
                               (hostel[0], room_type_id,)).fetchall()
    for hotel_room in db_hotel_rooms:
        with st.container():
            room_id = hotel_room[0]
            display_room(hotel_room)
            book_room_key = 'book_room' + str(room_id)
            if st.button('Забронировать номер', key=book_room_key):
                #room_bookings = c.execute("SELECT * FROM Room_book WHERE room_id + ?", (room_id,)).fetchall()
                #if
                c.execute("INSERT INTO Room_book (room_id, guest_id, check_in_date, eviction_date, status_id) "
                          "VALUES (?,?,?,?,?)", (room_id, guest_id, in_date, out_date, 1,))
                conn.commit()


def display_room(room):
    room_id = room[0]
    room_info = room_app.find_one({"_id": room_id})
    st.markdown(f'Номер комнаты: {room_info["number"]}')
    st.markdown(f'Этаж: {room_info["floor"]}')
    st.markdown(f'Количество кроватей: {room_info["beds"]}')
    st.markdown(f'Стоимость за ночь: {room[3]}')
    feature_str = ''
    room_features = c.execute("SELECT * FROM RoomFeatures WHERE room_id = ?", (room_id,)).fetchall()
    for feature in room_features:
        ftr = c.execute("SELECT feature_name FROM Feature WHERE feature_id = ?", (feature[1],)).fetchone()
        feature_str += ftr[0] + ', '
    st.markdown(f'Доп. услуги: {feature_str[:-2]}')


def registrate_guest():
    st.subheader('Введите ваши данные')
    with st.form(key='signup', clear_on_submit=True):
        guest_name = st.text_input('Имя')
        guest_surname = st.text_input('Фамилия')
        guest_login = st.text_input('Логин')
        guest_password = st.text_input('Пароль')
        guest_phone = st.text_input('Телефон')
        if st.form_submit_button('Зарегистрироваться'):
            try:
                c.execute("INSERT INTO Guest (guest_name, guest_surname, guest_login, guest_password, guest_phone)"
                          " VALUES (?,?,?,?,?)", (guest_name, guest_surname, guest_login, guest_password, guest_phone,))
                conn.commit()
                st.success('Новый пользователь успешно создан')
            except Exception as e:
                print(e)
                st.error('Не удалось созать нового пользователя. Проверьте введенные данные')


def settle_guest(guest_id, room_book_id):
    st.subheader('Введите паспортные данные гостя')
    check_data_key = 'check_data' + str(guest_id)
    form_key = 'add_passport' + str(guest_id)
    if st.button('Заселить', key=21321):
        status_id = c.execute("SELECT status_id FROM Room_book WHERE room_book_id = ?", (room_book_id,)).fetchone()[0]
        if status_id == 2:
            if passport_app.find_one({"_id": guest_id}):
                c.execute("UPDATE Room_book SET status_id = ? WHERE room_book_id = ?", (3, room_book_id,))
                conn.commit()
        else:
            st.error("Перед заселением необходимо оплатить счет и заполнить паспортные данные")
    if st.button('Проверить наличие данных', key=check_data_key):
        if passport_app.find_one({"_id": guest_id}):
            st.success('Паспортные данные уже имеются в системе')
        else:
            st.error('Паспортные данные не найдены, необходимо внести информацию!')
    with st.form(key=form_key, clear_on_submit=True):
        name = st.text_input('Имя')
        surname = st.text_input('Фамилия')
        patronymic = st.text_input('Отчество')
        date_of_bitrh = st.date_input('Дата рождения', min_value=date(year=1940, month=1, day=1))
        place_of_birth = st.text_input('Место рождения')
        col1, col2 = st.columns(2)
        with col1:
            serial_pass = st.text_input('Серия')
        with col2:
            number_pass = st.text_input('Номер')
        if st.form_submit_button('Добавить паспортные данные'):
            passport_app.insert_one({
                "_id": guest_id,
                "name": name,
                "surname": surname,
                "patronymic": patronymic,
                "birth_date": date_of_bitrh.__str__(),
                "birth_place": place_of_birth,
                "serial": serial_pass,
                "number": number_pass
            })
            st.success('Паспортные данные добавлены!')


if __name__ == '__main__':
    main()
