"""Сборка отчёта о НИР и отдельного документа ПМИ (DOCX), двухпроходная — для содержания.

Запуск: python3 src/build_report.py  (после analysis.py, export_matlab.py и построения рисунков matlab/make_all.m)
"""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import rep_app
import rep_ch1
import rep_ch2
import rep_ch3
import rep_ch4
import rep_ch5
import rep_ch6
import rep_front
from docbuilder import Report
from refs import REFS
from repdata import FIG, PHOTO, ROOT, Data

OUT = ROOT / "report"
NAME = "Отчёт_НИР_электротрактор_YL254ET.docx"
NAME_PMI = "ПМИ_электротрактор_YL254ET.docx"


# ------------------------------------------------------------------ фотографии
def compose(files, out, h=900, labels=True):
    ims = [Image.open(PHOTO / p).convert("RGB") for p in files]
    ims = [im.resize((int(im.width * h / im.height), h)) for im in ims]
    gap, lab = 30, (70 if labels and len(ims) > 1 else 0)
    W = sum(im.width for im in ims) + gap * (len(ims) - 1)
    canvas = Image.new("RGB", (W, h + lab), "white")
    x = 0
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", 48)
    except OSError:
        font = None
    for i, im in enumerate(ims):
        canvas.paste(im, (x, 0))
        if lab:
            d = ImageDraw.Draw(canvas)
            t = "абвгд"[i] + ")"
            d.text((x + im.width // 2 - 20, h + 8), t, fill="black", font=font)
        x += im.width + gap
    canvas.save(FIG / out, quality=88)


def photos():
    compose(["Фото заездов с навесным культиватором/Рисунок3.png"], "photo_cult.jpg", h=900, labels=False)
    compose(["Навесили фрезу культиваторную.jpeg", "Фото заездов с фрезой культиватором/54785b49-b3f5-4bc6-acbe-fab1f7ff120d.jpg"], "photo_till.jpg")
    shutil.copy(PHOTO / "Разбивка_опытного_участка.png", FIG / "photo_plot.png")
    compose(["Фото измерения плотности почвы/WhatsApp Image 2026-10-16 at 12.38.20 (1).jpeg",
             "Фото измерения влажности почвы/WhatsApp Image 2026-10-16 at 12.37.30.jpeg"], "photo_soil.jpg")
    compose(["Фотографии измерительного устройства для трактора/Интерфейсный адаптер CANable V2.jpg",
             "Фотографии измерительного устройства для трактора/WhatsApp Image 2026-10-16 at 12.52.59.jpeg"], "photo_can.jpg")
    compose(["Едем на опытный участок.jpeg", "Подключение и проверка к трактору.png"], "photo_app1.jpg")
    compose(["Рабочее место оператора регистрация телеметрии программой.jpg", "Рабочее окно программы.png"], "photo_app2.jpg")
    compose(["Вкладка поэлементного контроля тяговой батареи.png", "Зарядное устройство трактора.jpeg"], "photo_app3.jpg")
    compose(["Фото заездов с навесным культиватором/Рисунок2.png", "Фото заездов с навесным культиватором/Рисунок4.png"], "photo_app4.jpg")
    compose(["Фото заездов с фрезой культиватором/54785b49-b3f5-4bc6-acbe-fab1f7ff120d.jpg",
             "Фото измерения плотности почвы/WhatsApp Image 2026-10-16 at 12.37.29 (1).jpeg",
             "Фото измерения влажности почвы/WhatsApp Image 2026-10-16 at 12.38.21.jpeg"], "photo_app5.jpg")


# ------------------------------------------------------------------ сборка
def build(D, meta, pages=None):
    doc = Report(REFS)
    rep_front.title_page(doc)
    rep_front.executors(doc)
    rep_front.abstract(doc, meta, D)
    doc.struct("Содержание", toc=False)
    doc.toc_placeholder()
    rep_front.terms(doc)
    rep_front.abbreviations(doc)
    rep_front.introduction(doc, D)
    rep_ch1.build(doc, D)
    rep_ch2.build(doc, D)
    rep_ch3.build(doc, D)
    rep_ch4.build(doc, D)
    rep_ch5.build(doc, D)
    rep_ch6.build(doc, D)
    rep_ch6.conclusion(doc, D)
    doc.references()
    doc.appendix("А", "обязательное", "Программа и методика полевых испытаний")
    rep_app.pmi(doc, D, pre="А.")
    rep_app.app_passes(doc, D)
    rep_app.app_weights(doc, D)
    rep_app.app_params(doc, D)
    rep_app.app_photos(doc, D)
    rep_app.app_software(doc, D)
    doc.fill_toc(pages or [None] * len(doc.headings))
    return doc


def to_pdf(docx):
    d = Path(tempfile.mkdtemp())
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(d), str(docx)],
                   check=True, capture_output=True)
    return d / (Path(docx).stem + ".pdf")


def pdf_pages_text(pdf):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    return n, txt.split("\f")


def toc_end(pages_txt):
    """Индекс первой страницы после содержания (страницы содержания содержат строки с отточием)."""
    i = next(k for k, t in enumerate(pages_txt) if "СОДЕРЖАНИЕ" in t)
    while "....." in pages_txt[i]:
        i += 1
    return i


def find_pages(headings, pages_txt, start_after=3):
    """Номер страницы, на которой заголовок встречается как отдельная строка (после содержания)."""
    norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()
    out, cur = [], start_after
    for _, h in headings:
        key = norm(h)[:60]
        found = None
        for i in range(cur, len(pages_txt)):
            lines = [norm(x) for x in pages_txt[i].splitlines()]
            joined = " ".join(lines)
            if any(l.startswith(key[:40]) for l in lines) or key in joined:
                found = i + 1
                cur = i
                break
        out.append(found)
    return out


def main():
    OUT.mkdir(exist_ok=True)
    photos()
    D = Data()
    meta = {}
    doc = build(D, meta)
    p1 = OUT / NAME
    doc.save(p1)
    pdf = to_pdf(p1)
    n, txt = pdf_pages_text(pdf)
    # число страниц содержания влияет на нумерацию — два прохода
    for _ in range(2):
        pages = find_pages(doc.headings, txt, start_after=toc_end(txt))
        meta = {"pages": n, "figs": doc.counts["fig"], "tabs": doc.counts["tab"], "refs": len(doc.ref_order)}
        doc = build(D, meta, pages)
        doc.save(p1)
        pdf = to_pdf(p1)
        n, txt = pdf_pages_text(pdf)
    shutil.copy(pdf, OUT / (p1.stem + ".pdf"))
    print("отчёт:", n, "стр.,", meta, "заголовков без страницы:", sum(1 for x in pages if x is None))

    # отдельный документ ПМИ
    pm = Report(REFS)
    pmi_title(pm)
    rep_app.pmi(pm, D, pre="")
    pm.save(OUT / NAME_PMI)
    pdf2 = to_pdf(OUT / NAME_PMI)
    shutil.copy(pdf2, OUT / (Path(NAME_PMI).stem + ".pdf"))
    print("ПМИ:", pdf_pages_text(pdf2)[0], "стр.")


def pmi_title(doc):
    L = rep_front._line
    L(doc, "НАУЧНО-ПРОИЗВОДСТВЕННЫЙ ЦЕНТР АГРОИНЖЕНЕРИИ", bold=True, after=36)
    for t in ("УТВЕРЖДАЮ", "Руководитель организации", "_______________ / ______________ /", "«____» ______________ 2026 г."):
        L(doc, t, align="right")
    L(doc, "", after=60)
    L(doc, "ПРОГРАММА И МЕТОДИКА", bold=True, size=16)
    L(doc, "ПОЛЕВЫХ ИСПЫТАНИЙ", bold=True, size=16, after=18)
    L(doc, "электрического трактора JINMA YL254ET тягового класса 0,6 в агрегате с навесным культиватором "
           "и навесной культиваторной фрезой", after=100)
    for t in ("СОГЛАСОВАНО", "Руководитель НИР", "_______________ / ______________ /", "«____» ______________ 2026 г."):
        L(doc, t, align="left")
    L(doc, "", after=200)
    L(doc, "Алматы 2026")
    doc.pagebreak()


if __name__ == "__main__":
    main()
