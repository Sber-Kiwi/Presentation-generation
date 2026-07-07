from models import ObjectType

ALLOWED_OBJECT_TRANSFORMATION: dict[ObjectType, list[ObjectType]] = {
    ObjectType.TABLE: [ObjectType.TABLE],
    ObjectType.TEXT: [ObjectType.TEXT],
    ObjectType.BAR_CHART: [ObjectType.BAR_CHART, ObjectType.LINE_CHART],
    ObjectType.LINE_CHART: [ObjectType.BAR_CHART, ObjectType.LINE_CHART],
    ObjectType.PIE_CHART: [
        ObjectType.PIE_CHART,
        ObjectType.BAR_CHART,
        ObjectType.LINE_CHART,
    ],
    ObjectType.WATERFALL: [ObjectType.WATERFALL],
}
