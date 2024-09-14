import streamlit as st  # type: ignore
import numpy as np  # type: ignore

# Добавление стиля через HTML и CSS для улучшения UI
def add_custom_styles():
    st.markdown("""
        <style>
            .header-title {
                font-size: 32px;
                font-weight: bold;
                color: #4CAF50;
                text-align: center;
                margin-bottom: 20px;
            }
            .sub-header {
                font-size: 24px;
                font-weight: bold;
                color: #007BFF;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            .box {
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 10px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .result-box {
                padding: 10px;
                background-color: #E8F5E9;
                border-radius: 10px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .error-box {
                color: #FF0000;
                font-size: 18px;
                font-weight: bold;
            }
            .success-box {
                color: #4CAF50;
                font-size: 18px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

# Функция для расчета прибыли по каждому тейк-профиту
def calculate_profit(current_deposit, trade_size, take_profit_percent, sell_percent):
    price_increase = (take_profit_percent / 100) * trade_size
    profit = price_increase * (sell_percent / 100)
    return current_deposit + profit

# Функция для расчета убытка по стоп-лоссу
def calculate_stop_loss(deposit, trade_size, stop_loss_percent):
    loss = (stop_loss_percent / 100) * trade_size
    return max(deposit - loss, 0)

# Функция для валидации только **суммы процентов закрытия позиций** (sell_percent)
def validate_take_profits(take_profits):
    total_sell_percent = sum(tp["sell_percent"] for tp in take_profits)
    if total_sell_percent > 100:
        excess = total_sell_percent - 100
        return False, f"Общая сумма закрытых позиций превышает 100% на {excess:.2f}%."
    return True, ""

# Основная функция для калькулятора
def main():
    add_custom_styles()  # Добавляем кастомные стили
    st.markdown('<div class="header-title">Калькулятор тейк-профитов и стоп-лосса</div>', unsafe_allow_html=True)

    st.markdown('<div class="sub-header">📊 Ввод параметров сделки</div>', unsafe_allow_html=True)
    with st.expander("Введите данные сделки 💼"):
        trade_size = st.number_input("Сумма сделки ($)", value=5000, min_value=1000, step=100)
        deposit = st.number_input("Ваш депозит ($)", value=1000, min_value=100)
        stop_loss_percent = st.number_input("Процент для стоп-лосса (%)", min_value=0.1, max_value=50.0, value=1.48, step=0.1)

    st.markdown('<div class="sub-header">🎯 Тейк-профиты</div>', unsafe_allow_html=True)
    num_take_profits = st.number_input("Количество тейк-профитов", min_value=1, max_value=10, value=7, step=1)

    take_profits = []
    st.markdown('<div class="box">', unsafe_allow_html=True)
    for i in range(num_take_profits):
        # Процент роста цены может быть любым значением
        take_profit_percent = st.number_input(f"Процент до {i + 1}-го тейк-профита", min_value=0.1, max_value=1000.0, value=1.67 + i, step=0.1, key=f"tp_percent_{i}")
        # Проверяем только процент закрытия позиций (sell_percent), он должен быть <= 100%
        sell_percent = st.number_input(f"Процент закрытия на {i + 1}-м тейк-профите", min_value=1.0, max_value=100.0, value=20.0 if i < 3 else 10.0, step=1.0, key=f"tp_sell_{i}")
        take_profits.append({"take_profit_percent": take_profit_percent, "sell_percent": sell_percent})
    st.markdown('</div>', unsafe_allow_html=True)

    # Проверяем только сумму закрытых позиций
    is_valid, error_message = validate_take_profits(take_profits)
    if not is_valid:
        st.markdown(f'<div class="error-box">{error_message}</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="sub-header">💵 Результаты тейк-профитов</div>', unsafe_allow_html=True)
    results = []
    current_deposit = deposit
    for i, tp in enumerate(take_profits):
        before_profit = current_deposit
        current_deposit = calculate_profit(current_deposit, trade_size, tp["take_profit_percent"], tp["sell_percent"])
        results.append({"Тейк-профит": f"На уровне {tp['take_profit_percent']}%", "До тейк-профита": before_profit, "После тейк-профита": current_deposit})

    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.table(results)
    st.markdown('</div>', unsafe_allow_html=True)

    # Рассчитываем остаток на депозите после стоп-лосса
    deposit_after_stop_loss = calculate_stop_loss(deposit, trade_size, stop_loss_percent)
    st.markdown(f'<div class="success-box">После срабатывания стоп-лосса, если цена снизится на {stop_loss_percent}%, ваш депозит будет равен: ${deposit_after_stop_loss:.2f}</div>', unsafe_allow_html=True)

    # Рассчитываем RISK (убыток) и REWARD (прибыль)
    final_deposit_after_last_take = current_deposit  # Депозит после последнего тейк-профита
    risk = deposit - deposit_after_stop_loss  # Risk
    reward = final_deposit_after_last_take - deposit  # Reward

    # Проверяем, что RISK и REWARD не равны 0, чтобы избежать деления на 0
    if risk > 0:
        risk_reward_ratio = reward / risk if reward != 0 else float('inf')
    else:
        risk_reward_ratio = "Невозможно рассчитать (нет риска)"

    # Отображаем RISK/REWARD метрику
    st.markdown(f'<div class="sub-header">📈 Метрика Risk/Reward</div>', unsafe_allow_html=True)
    st.write(f"Risk (убыток): ${risk:.2f}")
    st.write(f"Reward (прибыль): ${reward:.2f}")
    st.write(f"Отношение Risk/Reward: {risk_reward_ratio:.2f}")

if __name__ == "__main__":
    main()
