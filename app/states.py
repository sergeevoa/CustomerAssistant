# Состояние - это метка на пользователе, позволяющая боту понять, что именно пользователь ему отправляет в данный момент
from aiogram.fsm.state import StatesGroup, State


# Класс состояния регистрации пользователя
class Reg(StatesGroup):                 # Cодержит поля (подсостояния)
    number = State()                    # Ввод номера телефона
    name = State()                      # Ввод имени


# Класс состояния редактирования аккаунта пользователя
class UserEditing(StatesGroup):
    name = State()
    phone_number = State()


# Класс состояния регистрации адреса
class Address(StatesGroup):
    district = State()                  # Ввод района
    street = State()                    # Ввод улицы
    home = State()                      # Ввод дома
    is_it_all = State()                 # Ввод ответа вопрос записывать ли подъезд и квартиру
    entrance = State()                  # Ввод подъезда
    apartment = State()                 # Ввод квартиры

    # Id ресторана, которому принадлежит адрес. Используется администраторами и владельцами ресторанов.
    restaurant_id = State()
    # Выбор места, для которого вводится адрес: ресторан или дом. Используется администраторами и владельцами ресторана
    choosing = State()


# Класс написания сообщения об ошибке пользователем
class TicketWriting(StatesGroup):
    text = State()                      # Ввод текста сообщения


# Класс состояния ответа администратора на пользовательское сообщение об ошибке
class TicketAnswer(StatesGroup):
    answer = State()                    # Ввод ответа для пользователя


# Класс состояний перехода пользователя по интерфейсу
class IntNavigation(StatesGroup):
    to_main = State()                   # Переход в главное меню


# Класс состояния редактирования категории ресторанов администратором
class CategoryEditing(StatesGroup):
    add_name = State()                  # Ввод названия для новой категории
    edit_name = State()                 # Изменение названия для существующей категории
    delete = State()                    # Удаление категории


# Класс состояния записи нового ресторана в БД администратором
class RestaurantAddition(StatesGroup):
    category_id = State()               # Запись категории ресторана
    name = State()                      # Ввод названия ресторана
    picture_link = State()              # Получение ссылки на фото ресторана
    address = State()                   # Ввод адреса ресторана


# Класс состояния редактирования ресторана администратором
class RestaurantEditing(StatesGroup):
    name = State()                      # Редактирование названия
    picture_link = State()              # Редактирование фото
    category = State()                  # Перенос в другую категорию
    delete = State()                    # Удаление ресторана


# Класс состояния записи новой категории блюд в БД администратором
class MealCategoryAddition(StatesGroup):
    category_id = State()               # Получение id ресторана, к которому относится категория
    name = State()                      # Ввод названия
    picture_link = State()              # Загрузка фотографии


# Класс состояния редактирования категории блюд администратором
class MealCategoryEditing(StatesGroup):
    name = State()                      # Изменение названия
    picture_link = State()              # Изменение фото
    delete = State()                    # Удаление категории


# Класс состояния записи нового блюда в БД администратором
class MealAddition(StatesGroup):
    category_id = State()               # Получение id категории, к которой относится блюдо
    name = State()                      # Ввод названия
    compound = State()                  # Ввод состава
    caloric_capacity = State()          # Ввод калорийности
    price = State()                     # Ввод цены
    picture_link = State()              # Загрузка фотографии


# Класс состояния редактирования блюда администратором
class MealEditing(StatesGroup):
    name = State()                      # Изменение названия
    compound = State()                  # Изменение состава
    caloric_capacity = State()          # Изменение калорийности
    price = State()                     # Изменение цены
    picture_link = State()              # Изменение фотографии


# Класс состояния стандартного добавления пользователя в БД
# Коды ролей: 0 - администратор, 1 - курьер, 2 - менеджер, 3 - владелец ресторана, 4 - пользователей
class CommonUserAddition(StatesGroup):
    role = State()
    name = State()
    surname = State()
    phone_number = State()
    tg_id = State()


# Класс состояния со специфическими подсостояниями, связанными с записью менеджера в БД
class ManagerAddition(StatesGroup):
    choose = State()                # Состояние выбора категории и ресторана, где работают менеджеры
    restaurant_id = State()         # Состояние сохранения restaurant_id менеджера


# Класс состояния редактирования информации об администраторе БД
class CommonUserEditing(StatesGroup):
    role = State()
    name = State()
    surname = State()
    phone_number = State()
    tg_id = State()


# Класс состояния оплаты заказа
class Payment(StatesGroup):
    payment = State()


# Класс состояния жалобы на перепутанный заказ
class WrongOrder(StatesGroup):
    order_id = State()
    order_photo = State()


# Класс состояния жалобы на потерявшегося курьера
class LostCourier(StatesGroup):
    order_id = State()
    text_courier = State()  # Состояние отправки сообщения пропавшему курьеру


# Класс состояния жалобы на грубого курьера
class AngryCourier(StatesGroup):
    order_id = State()


# Класс состояния взятия заказа менеджером
class ManagerWork(StatesGroup):
    restaurant_id = State()


# Класс состояния доставки заказа курьером
class CourierOrderDeliver(StatesGroup):
    delivering = State()
