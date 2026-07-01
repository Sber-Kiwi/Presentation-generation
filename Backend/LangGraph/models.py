from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

VERTICAL_SIZE = 3
HORIZONTAL_SIZE = 4


class PresentationNameAndMetricsList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    presentation_name: str = Field(description="Название презентации")
    metrics: list[str] = Field(
        description="Список показателей финансового анализа, выделенных из основного"
        " промпта. Нужен для состовления презентации. Первый элемент в списке -- название презентации."
    )


class PromptList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompts: list[str] = Field(
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
        description=f"Количество квадратов, которые объект занимает в ширину. От 1 до {HORIZONTAL_SIZE} минус номер колонки, в котором объект",
    )
    vertical_span: int = Field(
        ge=1,
        le=VERTICAL_SIZE,
        default=1,
        description=f"Количество квадратов, которые объект занимает в высоту. От 1 до {VERTICAL_SIZE} минус номер строки, в котором объект",
    )


class SlideItem(BaseModel):
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
