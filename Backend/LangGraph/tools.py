from langchain_core.tools import tool

import settings


@tool
def sql_query_dataframe(question: str) -> str:
    """
    Задает вопрос по DataFrame на естественном языке, генерирует SQL-запрос
    только с операцией SELECT, выполняет его на таблице sql_data и возвращает
    результат в виде CSV.

    Args:
        question (str): Вопрос на естественном языке о данных.
    """
    if settings.sql_data is None:
        return "SQL data is not defined, unable to make requests."

    sql_data = settings.sql_data

    sql_prompt = f"""
        Ты — SQL-генератор для анализа данных.
        Разрешен только один запрос SELECT.

        Схема таблицы sql_data:
        {list(settings.sql_data.columns)}

        Вопрос:
        {question}

        Ответь строго одним SQL-запросом.
        Запрещено:
        - писать пояснения;
        - использовать markdown;
        - использовать несколько запросов;
        - использовать INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, MERGE.

        Если для ответа нужен фильтр, агрегация или сортировка — используй только SELECT."""
    sql_request = settings.call_llm(
        llm=settings.llm, messages=sql_prompt
    ).content.strip()

    if ";" in sql_request:
        sql_request = sql_request.split(";")[0].strip()
    if (select_idx := sql_request.lower().find("select")) != -1:
        sql_request = sql_request[select_idx:]
    else:
        return "Запрещенная команда: агент может использовать только SELECT."

    sql_request = sql_request.replace("`", "'")

    try:
        result = settings.con.execute(sql_request).df()
    except Exception as e:
        return f"Ошибка выполнения SQL: {e}"

    return result.head(50).to_csv(index=False)


tools = [sql_query_dataframe]
