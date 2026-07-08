import seed from "../json-example.json";

const clone = (value) => JSON.parse(JSON.stringify(value));

// "База данных" мок-сервера. Живёт в памяти вкладки, сбрасывается при
// перезагрузке страницы — этого достаточно, чтобы обкатать все экраны
// загрузки, пока настоящего бэкенда нет.
export const db = {
  chats: clone(seed.chats), // [{ id, title, slides: [{ slideID, order, versions, state }] }]
};

let idCounter = 1000;
export function nextId(prefix) {
  idCounter += 1;
  return `${prefix}_${Date.now().toString(36)}_${idCounter}`;
}

export function findChat(chatId) {
  return db.chats.find((c) => c.id === chatId) || null;
}

export function findSlide(chatId, slideId) {
  const chat = findChat(chatId);
  if (!chat) return null;
  return chat.slides.find((s) => s.slideID === slideId) || null;
}

const OBJECT_TYPES = [
  "TEXT",
  "TABLE",
  "PIE_CHART",
  "BAR_CHART",
  "LINE_CHART",
  "WATERFALL",
];

function buildFakeSlide(index, prompt) {
  const slideID = nextId("slide");
  const versionID = nextId("version");
  return {
    slideID,
    order: index + 1,
    versions: [
      {
        versionID,
        slide: {
          meta: {
            slide_id: nextId("sld"),
            title:
              index === 0
                ? `Презентация: ${prompt.slice(0, 40)}`
                : `Слайд ${index + 1}`,
            notes: null,
          },
          objects: [
            {
              type: OBJECT_TYPES[index % OBJECT_TYPES.length],
              text: `Автосгенерированный блок ${index + 1}`,
              cell_pos: { x: 1, y: 1 },
              span: { x: 4, y: 2 },
            },
          ],
        },
        createdAt: new Date().toISOString(),
      },
    ],
    state: { selectedVersionID: versionID, inPresentation: true },
  };
}

// Имитация генерации презентации по промпту и csv-файлу (сам файл мок не
// читает — настоящий бэкенд будет анализировать таблицу).
export function buildFakeChat(prompt, fileName) {
  const slideCount = 3;
  const slides = Array.from({ length: slideCount }, (_, i) =>
    buildFakeSlide(i, prompt),
  );
  if (slides[0]) {
    slides[0].versions[0].slide.meta.notes = `Сгенерировано из файла ${fileName}`;
  }
  return {
    id: nextId("chat"),
    title: prompt.slice(0, 30) || "Новая презентация",
    slides,
  };
}

// Имитация правки слайда: клонируем текущую версию и добавляем в неё
// текстовый блок с содержимым правки, чтобы результат было видно на экране.
export function buildEditedVersion(baseVersion, prompt) {
  const versionID = nextId("version");
  const clonedSlide = clone(baseVersion.slide);
  clonedSlide.meta.notes = `Правка: ${prompt.slice(0, 80)}`;
  clonedSlide.objects.push({
    type: "TEXT_BOX",
    text: prompt.slice(0, 60),
    cell_pos: { x: 1, y: 3 },
    span: { x: 4, y: 1 },
  });
  return {
    versionID,
    slide: clonedSlide,
    createdAt: new Date().toISOString(),
  };
}
