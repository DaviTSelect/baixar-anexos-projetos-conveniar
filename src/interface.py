"""Interface gráfica (PySide6): baixar anexos de contratos por projeto.

Arquitetura:
- InterfaceAutomacao herda QWidget; é a janela principal.
- Threads se comunicam com a GUI via Queue + QTimer (100 ms), igual ao padrão anterior.
- _Label, _Button, _Entry expõem .configure() para compatibilidade com testes existentes.
- messagebox é um shim de módulo que encapsula QMessageBox.
- _AppProxy mantém self.app.destroy() e self.app.after() para os testes.

Para adicionar uma nova etapa ao cartão: crie um InputRow ou SelectionRow em
_montar_linhas() e trate o novo estado em atualizar_estado().
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread

# Garante que src/ está no sys.path quando o módulo é carregado por importlib
# (ex.: testes que usam spec_from_file_location sem passar por main.py)
_SRCDIR = str(Path(__file__).parent)
if _SRCDIR not in sys.path:
    sys.path.insert(0, _SRCDIR)

import openpyxl
from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QFrame, QGraphicsDropShadowEffect,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QVBoxLayout, QWidget,
)

from browser import realizar_login, buscar_contratos, processar_contrato
from config import BASE_DIR


# ──────────────────────────────────────────────────────────────
# Identidade visual  (mesma paleta do launcher e dos demais painéis)
# ──────────────────────────────────────────────────────────────

BG             = '#203447'
TEXT           = '#efede5'
ACTION         = '#e94c1f'
CARD_FOOT      = '#f1f1ed'
COR_DIVISOR    = '#415364'
COR_ICONE      = '#7a8791'
COR_SELECIONADO = '#317458'
_FUNDO_ICONE    = '#e9eef0'
_FUNDO_ICONE_OK = '#e5f4ed'


# ──────────────────────────────────────────────────────────────
# Shim de messagebox — mantém compatibilidade com testes que
# patcham `self.modulo.messagebox.showerror / showinfo`.
# ──────────────────────────────────────────────────────────────

class _MessageBox:
    @staticmethod
    def showerror(title='Erro', message='', parent=None, **_kw):
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def showinfo(title='', message='', parent=None, **_kw):
        QMessageBox.information(parent, title, message)

    @staticmethod
    def showwarning(title='', message='', parent=None, **_kw):
        QMessageBox.warning(parent, title, message)


messagebox = _MessageBox()


# ──────────────────────────────────────────────────────────────
# Proxy de app — mantém self.app.destroy() / self.app.after()
# exatamente como os testes esperam.
# ──────────────────────────────────────────────────────────────

class _AppProxy:
    def destroy(self):
        QApplication.quit()

    def after(self, _ms, _func):
        pass  # substituído por QTimer; mantido para API dos testes


# ──────────────────────────────────────────────────────────────
# Wrappers compatíveis — expõem .configure() sobre widgets Qt
# ──────────────────────────────────────────────────────────────

class _Label(QLabel):
    def configure(self, text='', **_kw):
        self.setText(str(text))


class _Button(QPushButton):
    def configure(self, state=None, text=None, **_kw):
        if state == 'disabled':
            self.setEnabled(False)
        elif state == 'normal':
            self.setEnabled(True)
        if text is not None:
            self.setText(str(text))


class _Entry(QLineEdit):
    def configure(self, state=None, **_kw):
        if state == 'disabled':
            self.setEnabled(False)
        elif state == 'normal':
            self.setEnabled(True)

    def get(self):
        return self.text()


# ──────────────────────────────────────────────────────────────
# Relatório Excel
# ──────────────────────────────────────────────────────────────

def gerar_relatorio(numero_projeto, resultados):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Relatorio"
    ws.append(["Projeto", "Contrato", "Situacao", "Resultado", "Anexos Baixados", "Detalhe"])
    for r in resultados:
        ws.append([r["projeto"], r["contrato"], r["situacao"],
                   r["resultado"], r["baixados"], r["detalhe"]])
    for col in ws.columns:
        largura = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(largura + 2, 60)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = BASE_DIR / f"relatorio_{numero_projeto}_{timestamp}.xlsx"
    wb.save(str(caminho))
    return caminho


# ──────────────────────────────────────────────────────────────
# Ícones vetoriais desenhados em grade 24×24
# ──────────────────────────────────────────────────────────────

class Icon(QWidget):
    """Ícone em traços vetoriais. ``kind``: 'folder', 'hash' ou 'check'."""

    def __init__(self, kind, color=COR_ICONE, size=24, parent=None):
        super().__init__(parent)
        self.kind, self.color = kind, color
        self.setFixedSize(size, size)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(self.width() / 24, self.height() / 24)
        pen = QPen(QColor(self.color), 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        if self.kind == 'folder':
            self._pasta(p)
        elif self.kind == 'hash':
            pen.setWidthF(1.5)
            p.setPen(pen)
            self._hash(p)
        elif self.kind == 'check':
            pen.setWidthF(2.0)
            p.setPen(pen)
            self._check(p)
        elif self.kind == 'monitor':
            self._monitor(p)
        p.end()

    @staticmethod
    def _ln(p, x1, y1, x2, y2):
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _monitor(self, p):
        # Tela
        path = QPainterPath()
        path.moveTo(3.5, 5.5)
        path.lineTo(20.5, 5.5)
        path.lineTo(20.5, 15.5)
        path.lineTo(3.5, 15.5)
        path.closeSubpath()
        p.drawPath(path)
        # Suporte
        self._ln(p, 12.0, 15.5, 12.0, 18.5)
        # Base
        self._ln(p, 8.5, 18.5, 15.5, 18.5)

    def _pasta(self, p):
        path = QPainterPath()
        path.moveTo(3.75, 16.25)
        path.lineTo(3.75, 6.75)
        path.cubicTo(3.75, 5.65, 4.65, 4.75, 5.75, 4.75)
        path.lineTo(9.11, 4.75)
        path.lineTo(11.91, 7.75)
        path.lineTo(18.25, 7.75)
        path.cubicTo(19.35, 7.75, 20.25, 8.65, 20.25, 9.75)
        path.lineTo(20.25, 16.25)
        path.cubicTo(20.25, 18, 19, 19.25, 17.25, 19.25)
        path.lineTo(6.75, 19.25)
        path.cubicTo(5, 19.25, 3.75, 18, 3.75, 16.25)
        p.drawPath(path)

    def _hash(self, p):
        self._ln(p, 9.0, 4.5,  7.0, 19.5)
        self._ln(p, 15.0, 4.5, 13.0, 19.5)
        self._ln(p, 4.5, 9.0,  19.5, 9.0)
        self._ln(p, 4.5, 15.0, 19.5, 15.0)

    @staticmethod
    def _check(p):
        path = QPainterPath()
        path.moveTo(6.75, 12.25)
        path.lineTo(10.0, 15.5)
        path.lineTo(17.25, 8.25)
        p.drawPath(path)


# ──────────────────────────────────────────────────────────────
# Helpers visuais
# ──────────────────────────────────────────────────────────────

def _rotulo(text, size, color, weight=QFont.Normal, wrap=False):
    w = QLabel(text)
    f = QFont('Segoe UI', size)
    f.setWeight(weight)
    w.setFont(f)
    w.setStyleSheet(f'color:{color};background:transparent;')
    if wrap:
        w.setWordWrap(True)
    return w


def _divisor(color='#e3e5e2'):
    d = QFrame()
    d.setFixedHeight(1)
    d.setStyleSheet(f'background:{color};border:none;')
    return d


def _porta_icone(ok=False):
    """Cria o quadrado arredondado de fundo do ícone."""
    f = QFrame()
    f.setFixedSize(43, 43)
    f.setStyleSheet(
        f'background:{_FUNDO_ICONE_OK if ok else _FUNDO_ICONE};border-radius:12px;')
    lay = QHBoxLayout(f)
    lay.setContentsMargins(0, 0, 0, 0)
    return f, lay


# ──────────────────────────────────────────────────────────────
# Linha de entrada de texto  (Número do projeto)
# ──────────────────────────────────────────────────────────────

class InputRow(QFrame):
    """Etapa com campo de texto inline para o número do projeto."""

    def __init__(self, number, title, description, placeholder, on_change):
        super().__init__()
        self._on_change = on_change
        self.setObjectName('inputRow')
        self.setStyleSheet('#inputRow{background:transparent;border:none;}')
        self.setMinimumHeight(118)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 20, 16, 20)
        outer.setSpacing(12)

        self._icon_holder, ih = _porta_icone(False)
        ih.addWidget(Icon('hash'))
        outer.addWidget(self._icon_holder, 0, Qt.AlignTop)

        content = QVBoxLayout()
        content.setSpacing(0)
        content.setContentsMargins(0, 1, 0, 0)

        head = QHBoxLayout()
        head.setSpacing(9)
        head.addWidget(_rotulo('ETAPA ' + number, 9, '#7b8791', QFont.Bold))
        self._status = QLabel('SELECIONADO')
        self._status.setFont(QFont('Segoe UI', 8))
        self._status.setStyleSheet(
            f'color:{COR_SELECIONADO};background:#e5f4ed;'
            'border-radius:9px;padding:3px 8px;')
        self._status.hide()
        head.addWidget(self._status)
        head.addStretch()
        content.addLayout(head)
        content.addSpacing(5)
        content.addWidget(_rotulo(title, 12, BG, QFont.DemiBold))
        content.addSpacing(4)
        content.addWidget(_rotulo(description, 10, '#6d7780', wrap=True))
        content.addSpacing(8)

        self._entry = _Entry()
        self._entry.setPlaceholderText(placeholder)
        self._entry.setFixedHeight(34)
        self._entry.setStyleSheet(
            'QLineEdit{background:#ffffff;border:1px solid #d9dddc;border-radius:8px;'
            'color:#344a5b;font:600 11px "Segoe UI";padding:0 10px;}'
            'QLineEdit:focus{border-color:#a0abb3;}'
            'QLineEdit:disabled{background:#f5f5f3;color:#a0a8ae;}')
        self._entry.textChanged.connect(self._ao_mudar)
        content.addWidget(self._entry)
        content.addStretch()
        outer.addLayout(content, 1)

    def _ao_mudar(self, text):
        ok = bool(text.strip())
        self._status.setVisible(ok)
        lay = self._icon_holder.layout()
        old = lay.takeAt(0)
        if old and old.widget():
            old.widget().deleteLater()
        lay.addWidget(Icon('check' if ok else 'hash',
                           COR_SELECIONADO if ok else COR_ICONE))
        self._icon_holder.setStyleSheet(
            f'background:{_FUNDO_ICONE_OK if ok else _FUNDO_ICONE};border-radius:12px;')
        self._on_change()

    def valor(self):
        return self._entry.text().strip()

    def configure(self, state=None, **_kw):
        self._entry.configure(state=state)


# ──────────────────────────────────────────────────────────────
# Linha de seleção de pasta
# ──────────────────────────────────────────────────────────────

class SelectionRow(QFrame):
    """Etapa com diálogo de seleção de pasta."""

    def __init__(self, number, title, description, button_text, choose):
        super().__init__()
        self._btn_text = button_text
        self.setObjectName('selRow')
        self.setStyleSheet('#selRow{background:transparent;border:none;}')
        self.setMinimumHeight(118)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 20, 16, 20)
        outer.setSpacing(12)

        self._icon_holder, ih = _porta_icone(False)
        ih.addWidget(Icon('folder'))
        outer.addWidget(self._icon_holder, 0, Qt.AlignTop)

        content = QVBoxLayout()
        content.setSpacing(0)
        content.setContentsMargins(0, 1, 0, 0)

        head = QHBoxLayout()
        head.setSpacing(9)
        head.addWidget(_rotulo('ETAPA ' + number, 9, '#7b8791', QFont.Bold))
        self._status = QLabel('SELECIONADO')
        self._status.setFont(QFont('Segoe UI', 8))
        self._status.setStyleSheet(
            f'color:{COR_SELECIONADO};background:#e5f4ed;border-radius:9px;padding:3px 8px;')
        self._status.hide()
        head.addWidget(self._status)
        head.addStretch()
        content.addLayout(head)
        content.addSpacing(5)
        content.addWidget(_rotulo(title, 12, BG, QFont.DemiBold))
        content.addSpacing(4)
        content.addWidget(_rotulo(description, 10, '#6d7780', wrap=True))
        self._valor = _rotulo('', 10, '#344b5e', QFont.Medium)
        self._valor.hide()
        content.addSpacing(4)
        content.addWidget(self._valor)
        content.addStretch()
        outer.addLayout(content, 1)

        self.button = _Button(button_text)
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setMinimumWidth(130)
        self.button.setFixedHeight(39)
        self.button.setStyleSheet(
            'QPushButton{background:#ffffff;border:1px solid #d9dddc;border-radius:9px;'
            'color:#344a5b;font:600 11px "Segoe UI";padding:0 12px;}'
            'QPushButton:hover{background:#f1f3f1;border-color:#b5bec3;}')
        self.button.clicked.connect(choose)
        outer.addWidget(self.button, 0, Qt.AlignVCenter)

    def definir_valor(self, value):
        ok = bool(value)
        self._status.setVisible(ok)
        self._valor.setText(value)
        self._valor.setToolTip(value)
        self._valor.setVisible(ok)
        self.button.setText('Alterar' if ok else self._btn_text)
        lay = self._icon_holder.layout()
        old = lay.takeAt(0)
        if old and old.widget():
            old.widget().deleteLater()
        lay.addWidget(Icon('check' if ok else 'folder',
                           COR_SELECIONADO if ok else COR_ICONE))
        self._icon_holder.setStyleSheet(
            f'background:{_FUNDO_ICONE_OK if ok else _FUNDO_ICONE};border-radius:12px;')

    def configure(self, state=None, **_kw):
        self.button.configure(state=state)


# ──────────────────────────────────────────────────────────────
# Linha de alternância (checkbox visual)
# ──────────────────────────────────────────────────────────────

class ToggleRow(QFrame):
    """Etapa com alternância (ativo/inativo) baseada em QCheckBox."""

    def __init__(self, number, title, description, label, changed_cb, optional=True):
        super().__init__()
        self.setObjectName('togRow')
        self.setStyleSheet('#togRow{background:transparent;border:none;}')
        self.setMinimumHeight(100)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        self._icon_holder, ih = _porta_icone(False)
        ih.addWidget(Icon('monitor'))
        outer.addWidget(self._icon_holder, 0, Qt.AlignTop)

        content = QVBoxLayout()
        content.setSpacing(0)
        content.setContentsMargins(0, 1, 0, 0)

        head = QHBoxLayout()
        head.setSpacing(9)
        head.addWidget(_rotulo('ETAPA ' + number, 9, '#7b8791', QFont.Bold))
        if optional:
            opt = QLabel('OPCIONAL')
            opt.setFont(QFont('Segoe UI', 8))
            opt.setStyleSheet(
                'color:#8998a3;background:#edf0ee;border-radius:9px;padding:3px 8px;')
            head.addWidget(opt)
        head.addStretch()
        content.addLayout(head)
        content.addSpacing(5)
        content.addWidget(_rotulo(title, 12, BG, QFont.DemiBold))
        content.addSpacing(4)
        content.addWidget(_rotulo(description, 10, '#6d7780', wrap=True))
        content.addStretch()
        outer.addLayout(content, 1)

        self._toggle = QCheckBox(label)
        self._toggle.setFont(QFont('Segoe UI', 10))
        self._toggle.setCursor(Qt.PointingHandCursor)
        self._toggle.setStyleSheet(
            'QCheckBox{color:#344a5b;spacing:8px;}'
            'QCheckBox::indicator{width:18px;height:18px;border:2px solid #c0c8cc;'
            'border-radius:4px;background:#ffffff;}'
            'QCheckBox::indicator:checked{background:#317458;border-color:#317458;}'
            'QCheckBox::indicator:hover{border-color:#8ea8b4;}')
        self._toggle.stateChanged.connect(lambda _s: changed_cb(self._toggle.isChecked()))
        outer.addWidget(self._toggle, 0, Qt.AlignVCenter)

    def marcado(self) -> bool:
        return self._toggle.isChecked()

    def configure(self, state=None, **_kw):
        if state == 'disabled':
            self._toggle.setEnabled(False)
        elif state == 'normal':
            self._toggle.setEnabled(True)


# ──────────────────────────────────────────────────────────────
# Janela principal
# ──────────────────────────────────────────────────────────────

class InterfaceAutomacao(QWidget):
    """Janela principal: configuração do projeto, execução e acompanhamento."""

    def __init__(self):
        _qapp = QApplication.instance() or QApplication(sys.argv)
        super().__init__()

        # Proxy de compatibilidade com testes que verificam self.app.destroy()
        self.app = _AppProxy()

        self.setWindowTitle('Baixar Anexos – Contratos por Projeto')
        self.resize(940, 590)
        self.setMinimumSize(800, 530)
        self.setStyleSheet(f'background:{BG};')

        base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
        icon_path = base / 'icon' / 'logo.ico'
        if icon_path.is_file():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Estado da automação
        self.numero_projeto: int | None = None
        self.diretorio: Path | None = None
        self.ocultar_chrome = False
        self.executando = False
        self.fechando = False
        self.cancelar = Event()
        self.worker: Thread | None = None
        self.eventos: Queue = Queue()

        self._montar_ui()

        # QTimer substitui app.after(100, consumir_eventos)
        self._timer_eventos = QTimer(self)
        self._timer_eventos.timeout.connect(self.consumir_eventos)
        self._timer_eventos.start(100)

    # ----------------------------------------------------------------
    # API pública  (chamada por main.py)
    # ----------------------------------------------------------------

    def iniciar(self):
        self.show()
        QApplication.instance().exec()

    # ----------------------------------------------------------------
    # Montagem da interface
    # ----------------------------------------------------------------

    def _montar_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 22, 44, 22)
        root.setSpacing(0)
        self._montar_cabecalho(root)
        center = QHBoxLayout()
        center.setSpacing(60)
        center.addLayout(self._painel_esquerdo(), 4)
        center.addWidget(self._cartao(), 7)
        root.addLayout(center, 1)
        self._montar_rodape_janela(root)

    def _montar_cabecalho(self, root):
        hdr = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(4)
        titulos.addWidget(_rotulo('G E S T Ã O   O P E R A C I O N A L', 9, '#85929c', QFont.Bold))
        titulos.addWidget(_rotulo('Baixar Anexos', 14, TEXT, QFont.DemiBold))
        hdr.addLayout(titulos)
        hdr.addStretch()
        self._dot_versao = QLabel('●')
        self._dot_versao.setFont(QFont('Segoe UI', 14))
        self._dot_versao.setStyleSheet('color:#e9b44c;background:transparent;')
        hdr.addWidget(self._dot_versao)
        self._txt_versao = _rotulo('', 10, '#a0aab1', QFont.Medium)
        hdr.addWidget(self._txt_versao)
        self._atualizar_indicador_versao()
        root.addLayout(hdr)
        root.addSpacing(18)
        root.addWidget(_divisor(COR_DIVISOR))

    def _atualizar_indicador_versao(self):
        try:
            from version import VERSION
            self._txt_versao.setText(f'v{VERSION} · Atualizado')
            self._dot_versao.setStyleSheet('color:#53b88c;background:transparent;font-size:14px;')
        except Exception:
            self._txt_versao.setText('versão não disponível')
            self._dot_versao.setStyleSheet('color:#85929c;background:transparent;font-size:14px;')

    def _painel_esquerdo(self):
        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        left.addStretch()
        left.addWidget(_rotulo('B A I X A R   A N E X O S', 9, ACTION, QFont.Bold))
        left.addSpacing(18)
        titulo = _rotulo('Contratos\npor projeto.', 28, TEXT, QFont.DemiBold, wrap=True)
        left.addWidget(titulo)
        left.addSpacing(20)
        intro = _rotulo(
            'Informe o número do projeto e selecione a pasta de destino. '
            'O sistema buscará todos os contratos ativos e encerrados '
            'e baixará os anexos automaticamente.',
            11, '#a5afb6', wrap=True)
        intro.setMaximumWidth(315)
        left.addWidget(intro)
        left.addSpacing(32)
        left.addWidget(_divisor(COR_DIVISOR))
        left.addSpacing(20)
        seg = QHBoxLayout()
        seg.setSpacing(12)
        circulo = QFrame()
        circulo.setFixedSize(34, 34)
        circulo.setStyleSheet('background:#304658;border-radius:17px;')
        cl = QHBoxLayout(circulo)
        cl.setContentsMargins(5, 5, 5, 5)
        cl.addWidget(Icon('hash', '#a6b4bd', 20))
        seg.addWidget(circulo, 0, Qt.AlignTop)
        seg.addWidget(_rotulo(
            'Os arquivos são processados localmente e não são compartilhados.',
            10, '#8998a3', wrap=True), 1)
        left.addLayout(seg)
        left.addStretch()
        return left

    def _cartao(self):
        card = QFrame()
        card.setObjectName('card')
        card.setStyleSheet('#card{background:#f8f7f3;border-radius:18px;}')
        sombra = QGraphicsDropShadowEffect(card)
        sombra.setBlurRadius(50)
        sombra.setOffset(0, 20)
        sombra.setColor(QColor(6, 18, 28, 75))
        card.setGraphicsEffect(sombra)
        lay = QVBoxLayout(card)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        self._montar_titulo_cartao(lay)
        lay.addWidget(_divisor('#dde1df'))
        self._montar_linhas(lay)
        self._montar_rodape_cartao(lay)
        return card

    def _montar_titulo_cartao(self, lay):
        topo = QHBoxLayout()
        topo.setContentsMargins(28, 16, 28, 16)
        titulos = QVBoxLayout()
        titulos.setSpacing(4)
        titulos.addWidget(_rotulo('Configurar download', 14, BG, QFont.DemiBold))
        titulos.addWidget(_rotulo('Preencha as etapas para continuar', 10, '#7a838a'))
        topo.addLayout(titulos)
        topo.addStretch()
        self._contador = QLabel('0 de 2')
        self._contador.setFont(QFont('Segoe UI', 9))
        self._contador.setStyleSheet(
            'color:#68747d;background:transparent;border:1px solid #d9dddc;'
            'border-radius:12px;padding:7px 12px;')
        topo.addWidget(self._contador)
        lay.addLayout(topo)

    def _montar_linhas(self, lay):
        # Etapa 01 — número do projeto (campo de texto)
        self._row_projeto = InputRow(
            '01', 'Número do projeto',
            'Digite o número do projeto para buscar os contratos.',
            'Ex.: 12345',
            self._ao_mudar_selecoes,
        )
        # campo_N_projeto é o QLineEdit interno, mantido para compatibilidade com testes
        self.campo_N_projeto = self._row_projeto._entry
        lay.addWidget(self._row_projeto)
        lay.addWidget(_divisor('#e3e5e2'))

        # Etapa 02 — pasta de downloads
        self._row_pasta = SelectionRow(
            '02', 'Pasta de downloads',
            'Escolha onde os anexos dos contratos serão salvos.',
            'Selecionar pasta',
            self._escolher_pasta,
        )
        lay.addWidget(self._row_pasta)
        lay.addWidget(_divisor('#e3e5e2'))

        # Etapa 03 — ocultar janela do Chrome (opcional)
        self._row_headless = ToggleRow(
            '03', 'Modo silencioso',
            'Oculta a janela do Chrome durante a execução.',
            'Ocultar Chrome',
            self._ao_mudar_headless,
        )
        lay.addWidget(self._row_headless)

    def _montar_rodape_cartao(self, lay):
        rodape = QFrame()
        rodape.setStyleSheet(
            f'background:{CARD_FOOT};'
            'border-bottom-left-radius:18px;border-bottom-right-radius:18px;')
        rl = QHBoxLayout(rodape)
        rl.setContentsMargins(28, 18, 28, 18)

        textos = QVBoxLayout()
        textos.setSpacing(4)
        self._status_titulo = _rotulo('Aguardando configurações', 10, '#344a5b', QFont.DemiBold)
        # label_status é o atributo usado em executar_automacao (via eventos)
        self.label_status = _Label('Complete as etapas acima para continuar.')
        self.label_status.setFont(QFont('Segoe UI', 9))
        self.label_status.setStyleSheet('color:#838c91;background:transparent;')
        self.label_status.setWordWrap(True)
        textos.addWidget(self._status_titulo)
        textos.addWidget(self.label_status)
        rl.addLayout(textos, 1)

        # botao_conferir_N_projeto mantido para compatibilidade com testes
        self.botao_conferir_N_projeto = _Button('Iniciar download   →')
        self.botao_conferir_N_projeto.setFixedHeight(46)
        self.botao_conferir_N_projeto.setMinimumWidth(185)
        self.botao_conferir_N_projeto.setCursor(Qt.PointingHandCursor)
        self.botao_conferir_N_projeto.clicked.connect(self.botao_conferir_Projeto)
        self._definir_estilo_botao(ativo=False)
        rl.addWidget(self.botao_conferir_N_projeto)
        lay.addWidget(rodape)

    def _montar_rodape_janela(self, root):
        root.addWidget(_divisor(COR_DIVISOR))
        root.addSpacing(14)
        bottom = QHBoxLayout()
        bottom.addWidget(_rotulo('Baixar Anexos – Contratos por Projeto', 9, '#83919c'))
        bottom.addStretch()
        bottom.addWidget(_rotulo('Ambiente seguro', 9, '#83919c'))
        root.addLayout(bottom)

    # ----------------------------------------------------------------
    # Estado
    # ----------------------------------------------------------------

    def _definir_estilo_botao(self, ativo: bool):
        if ativo:
            self.botao_conferir_N_projeto.setStyleSheet(
                f'QPushButton{{background:{ACTION};color:white;border:none;'
                'border-radius:9px;font:600 11px "Segoe UI";padding:0 19px;}}'
                'QPushButton:hover{background:#d74118;}')
        else:
            self.botao_conferir_N_projeto.setStyleSheet(
                'QPushButton{background:#d8dad9;color:#92999b;border:none;'
                'border-radius:9px;font:600 11px "Segoe UI";padding:0 19px;}')
        self.botao_conferir_N_projeto.setEnabled(ativo)

    def _ao_mudar_selecoes(self):
        self.atualizar_estado()

    def _ao_mudar_headless(self, marcado: bool):
        self.ocultar_chrome = marcado

    def atualizar_estado(self):
        n = self._row_projeto.valor() if hasattr(self, '_row_projeto') else ''
        d = self.diretorio
        pronto = bool(n) and n.isdigit() and d is not None
        total = sum([bool(n), d is not None])
        if hasattr(self, '_contador'):
            self._contador.setText(f'{total} de 2')
        pode_iniciar = pronto and not self.executando and not self.fechando
        self._definir_estilo_botao(pode_iniciar)
        if not self.executando:
            if pronto:
                if hasattr(self, '_status_titulo'):
                    self._status_titulo.setText('Tudo pronto para começar')
                self.label_status.configure(text='Revise e clique para iniciar o download.')
            else:
                if hasattr(self, '_status_titulo'):
                    self._status_titulo.setText('Aguardando configurações')
                self.label_status.configure(text='Complete as etapas acima para continuar.')

    def atualizar_status(self, texto):
        self.label_status.configure(text=texto)

    # ----------------------------------------------------------------
    # Seleção de pasta
    # ----------------------------------------------------------------

    def _escolher_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, 'Selecionar pasta de downloads')
        if pasta:
            self.diretorio = Path(pasta)
            self._row_pasta.definir_valor(Path(pasta).name or pasta)
            self.atualizar_estado()

    # ----------------------------------------------------------------
    # Botão principal
    # ----------------------------------------------------------------

    def botao_conferir_Projeto(self):
        if self.executando or self.fechando:
            return
        texto = self._row_projeto.valor()
        if not texto.isdigit():
            messagebox.showerror(
                title='ERRO',
                message='Erro no valor inserido!\n\nPor favor, escreva apenas números.',
            )
            return
        self.numero_projeto = int(texto)
        if not self.diretorio:
            messagebox.showwarning(
                title='Pasta não selecionada',
                message='Selecione a pasta de downloads antes de continuar.',
            )
            return
        self.botao_iniciar_processo()

    def botao_iniciar_processo(self):
        if self.executando or self.fechando:
            return
        self.executando = True
        self.cancelar.clear()
        self.botao_conferir_N_projeto.configure(state='disabled')
        self.campo_N_projeto.configure(state='disabled')
        if hasattr(self, '_row_pasta'):
            self._row_pasta.configure(state='disabled')
        if hasattr(self, '_row_headless'):
            self._row_headless.configure(state='disabled')
        if hasattr(self, '_status_titulo'):
            self._status_titulo.setText('Processamento em andamento')
        self.worker = Thread(
            target=self.executar_automacao,
            args=(self.numero_projeto, self.diretorio),
            daemon=False,
        )
        self.worker.start()

    # ----------------------------------------------------------------
    # Automação (thread separada — só fala com a GUI via Queue)
    # ----------------------------------------------------------------

    def executar_automacao(self, numero_projeto, diretorio):
        driver = None
        etapa = 'login'
        erro = None
        texto = 'Processamento interrompido.'
        resultados_contratos = []
        try:
            if self.cancelar.is_set():
                return
            self.eventos.put(('status', 'Realizando login...'))
            driver = realizar_login(headless=getattr(self, 'ocultar_chrome', False))
            if self.cancelar.is_set():
                return
            etapa = 'configuração da pasta de downloads'
            diretorio.mkdir(parents=True, exist_ok=True)
            driver.execute_cdp_cmd('Browser.setDownloadBehavior', {
                'behavior': 'allow', 'downloadPath': str(diretorio.resolve()),
            })
            etapa = 'consulta dos contratos'
            self.eventos.put(('status', 'Buscando contratos...'))
            resultados = buscar_contratos(driver, numero_projeto)
            for item in resultados:
                if self.cancelar.is_set():
                    return
                etapa = f"contrato {item['contrato']}"
                self.eventos.put(('status', f"Baixando anexos do contrato {item['contrato']}..."))
                try:
                    r = processar_contrato(driver, item, numero_projeto, diretorio)
                    if r.get('sem_tabela'):
                        resultado_texto = 'Sem anexos'
                        detalhe = 'Tabela de arquivos não encontrada'
                    elif r['baixados'] == 0:
                        resultado_texto = 'Sem anexos'
                        detalhe = ''
                    else:
                        resultado_texto = 'Sucesso'
                        detalhe = ''
                    resultados_contratos.append({
                        'projeto': numero_projeto,
                        'contrato': item['contrato'],
                        'situacao': item.get('status', ''),
                        'resultado': resultado_texto,
                        'baixados': r['baixados'],
                        'detalhe': detalhe,
                    })
                except Exception as e_contrato:
                    resultados_contratos.append({
                        'projeto': numero_projeto,
                        'contrato': item['contrato'],
                        'situacao': item.get('status', ''),
                        'resultado': 'Erro',
                        'baixados': 0,
                        'detalhe': str(e_contrato),
                    })
            if not resultados:
                texto = 'Nenhum contrato encontrado.'
            else:
                erros = sum(1 for r in resultados_contratos if r['resultado'] == 'Erro')
                texto = 'Downloads concluídos.'
                if erros:
                    texto += f' ({erros} contrato(s) com erro)'
                try:
                    etapa = 'geração do relatório'
                    caminho = gerar_relatorio(numero_projeto, resultados_contratos)
                    texto += f'\nRelatório: {caminho.name}'
                except Exception:
                    texto += '\nFalha ao gerar relatório.'
        except Exception:
            erro = f'Falha no processamento: {etapa}.'
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    erro = erro or 'Falha ao encerrar o navegador.'
            self.eventos.put(('fim', (texto, erro)))

    # ----------------------------------------------------------------
    # Consumo de eventos (thread principal via QTimer)
    # ----------------------------------------------------------------

    def consumir_eventos(self):
        try:
            while True:
                tipo, dados = self.eventos.get_nowait()
                if tipo == 'status' and not self.fechando:
                    self.atualizar_status(dados)
                elif tipo == 'fim':
                    self.executando = False
                    if not self.fechando:
                        texto, erro = dados
                        self.botao_conferir_N_projeto.configure(state='normal')
                        self.campo_N_projeto.configure(state='normal')
                        if hasattr(self, '_row_pasta'):
                            self._row_pasta.configure(state='normal')
                        if hasattr(self, '_row_headless'):
                            self._row_headless.configure(state='normal')
                        if hasattr(self, '_status_titulo'):
                            self._status_titulo.setText('Concluído' if not erro else 'Falha')
                        self.atualizar_status(erro or texto)
                        self.atualizar_estado()
                        if erro:
                            messagebox.showerror(title='Erro', message=erro)
                        else:
                            messagebox.showinfo(title='Conclusão', message=texto)
        except Empty:
            pass
        if self.fechando and (self.worker is None or not self.worker.is_alive()):
            if hasattr(self, '_timer_eventos'):
                self._timer_eventos.stop()
            self.app.destroy()

    # ----------------------------------------------------------------
    # Fechamento cooperativo
    # ----------------------------------------------------------------

    def fechar(self):
        self.fechando = True
        self.cancelar.set()
        self.botao_conferir_N_projeto.configure(state='disabled')
        self.atualizar_status(
            'Encerrando: aguardando a operação atual e fechando o navegador...')

    def closeEvent(self, event):
        if self.executando:
            self.fechar()
            event.ignore()
        else:
            if hasattr(self, '_timer_eventos'):
                self._timer_eventos.stop()
            event.accept()
