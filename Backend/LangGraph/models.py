from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

VERTICAL_SIZE = 3
HORIZONTAL_SIZE = 4

SlideNum = int
SlideVersion = int
UserChangePrompt = str

Json = Annotated[dict, "This is a dict representing json"]


class PresentationNameAndMetricsList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    presentation_name: str = Field(description="Название презентации")
    metrics: list[str] = Field(
        description="Список показателей финансового анализа, выделенных из основного"
        " промпта. Нужен для состовления презентации. Первый элемент в списке -- название презентации."
    )


class PromptSlide(BaseModel):
    slide_name: str = Field(description="Название слайда (заголовок)")
    idea: str = Field(
        description="Короткий аналитический тезис, который слайд должен донести"
    )
    contents: str = Field(
        description="Перечень объектов на слайде: тип каждого объекта (таблица, "
        "график, текст), что именно он отображает"
    )


class PromptList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompts: list[PromptSlide] = Field(
        description="Список промптов для нейронной сети для каждого слайда презентации."
        " Содержит словесное описание содержания слайда."
    )


class ObjectType(str, Enum):
    TEXT = "TEXT"
    TABLE = "TABLE"
    PIE_CHART = "PIE_CHART"
    BAR_CHART = "BAR_CHART"
    LINE_CHART = "LINE_CHART"
    WATERFALL = "WATERFALL"


class ObjectPosition(BaseModel):
    x: int = Field(
        ge=1,
        le=HORIZONTAL_SIZE,
        description=f"Номер колонки, в которой находится начало объекта. От 1 до {HORIZONTAL_SIZE}",
    )
    y: int = Field(
        ge=1,
        le=VERTICAL_SIZE,
        description=f"Номер строчки, в которой находится начало объекта. От 1 до {VERTICAL_SIZE}",
    )


class ObjectSpan(BaseModel):
    horizontal_span: int = Field(
        ge=1,
        le=HORIZONTAL_SIZE,
        default=1,
        description="Количество квадратов, которые объект занимает в ширину. "
        f" От 1 до {HORIZONTAL_SIZE} минус номер колонки, в котором объект",
    )
    vertical_span: int = Field(
        ge=1,
        le=VERTICAL_SIZE,
        default=1,
        description=f"Количество квадратов, которые объект занимает в высоту."
        f" От 1 до {VERTICAL_SIZE} минус номер строки, в котором объект",
    )


class SlideItem(BaseModel):
    id: int = Field(description="Уникальный идентификатор объекта на слайде")
    type: ObjectType = Field(description="Тип графика")
    prompt: str = Field(description="Словесное описание данных для графика")
    position: ObjectPosition = Field(
        description="Расположение верхнего левого угла объекта"
    )
    span: ObjectSpan = Field(
        default_factory=ObjectSpan,
        description="Размер объекта в сетке слайда -- сколько квадратов он занимает. По умолчанию 1 на 1",
    )


class DraftSlide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Заголовок слайда")
    objects: list[SlideItem] = Field(
        description="Список всех объектов -- текста, графиков, таблиц -- на слайде.",
    )


class TextData(BaseModel):
    kind: Literal["TextData"] = "TextData"
    text: str = Field(description="Текст в формате Markdown")


class TableData(BaseModel):
    kind: Literal["TableData"] = "TableData"
    headers: list[str] = Field(description="Список заголовков колонок таблицы")
    rows: list[list[str | int | float]] = Field(
        description="Строки с данными, порядок значений в каждой строке "
        "соответствует порядку заголовков"
    )
    caption: str | None = Field(default=None, description="Заголовок всей таблицы")


class ChartType(str, Enum):
    LINE = "LINE"
    BAR = "BAR"
    PIE = "PIE"


class ChartPoint(BaseModel):
    x: str = Field(description="Значение по оси X (для PIE -- название сектора)")
    y: int | float = Field(
        description="Значение по оси Y (для PIE -- значение сектора)"
    )


class ChartSeries(BaseModel):
    unit: str = Field(description="Подпись группы данных")
    data: list[ChartPoint] = Field(description="Список точек данных для графика")
    # color заполняется в коде по собственной палитре, LLM его не выбирает


class ChartData(BaseModel):
    kind: Literal["ChartData"] = "ChartData"
    title: str = Field(description="Заголовок графика")
    chart_type: ChartType = Field(description="Тип графика: LINE, BAR или PIE")
    series: list[ChartSeries] = Field(
        description="Данные для графика, с разбиением по группам (сериям)"
    )


class WaterfallItemType(str, Enum):
    START = "START"
    COMMON = "COMMON"
    END = "END"


class WaterfallItem(BaseModel):
    type: WaterfallItemType = Field(
        description="Тип столбца: COMMON показывает изменение, "
        "START и END - весь столбец"
    )
    name: str = Field(description="Подпись столбца")
    plan: int | float = Field(description="Плановое значение")
    fact: int | float = Field(
        description="Фактическое значение -- используется для вычисления delta в коде"
    )
    text: str | None = Field(
        description="Объяснение для данных столбца, которое будет отображаться рядом с графиком"
    )
    # delta вычисляется функционально из plan/fact, LLM его не заполняет


class WaterfallData(BaseModel):
    kind: Literal["WaterfallData"] = "WaterfallData"
    data: list[WaterfallItem] = Field(description="Данные для графика")


# Discriminated union for the "data" field on each object
FinalObjectData = Annotated[
    Union[TextData, TableData, ChartData, WaterfallData],
    Field(discriminator="kind"),
]


class FinalSlideData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objects: dict[int, FinalObjectData] = Field(
        description="Список всех объектов -- текста, графиков, таблиц -- на слайде с соотвествующими идентификаторами.",
    )
