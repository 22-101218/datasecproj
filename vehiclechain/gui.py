import os
import sys, threading, time
from datetime import datetime
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from web3 import Web3
from vehiclechain.audit_log import get_log_path, log_action, read_log
from vehiclechain.paths import logo_path
from vehiclechain.vin_utils import validate_vehicle_id

try:
    import vehiclechain.blockchain as bc
    _BLOCKCHAIN_ERROR: Optional[Exception] = None
except Exception as exc:
    bc = None
    _BLOCKCHAIN_ERROR = exc


def pixmap_from_png(path: Path) -> QPixmap:
    """Load PNG reliably (QPixmap(path) often fails for PyInstaller + Unicode paths on Windows)."""
    try:
        if path.is_file():
            img = QImage.fromData(path.read_bytes(), "PNG")
            if not img.isNull():
                return QPixmap.fromImage(img)
        # Fallback: try direct QPixmap loading
        pix = QPixmap(str(path))
        if not pix.isNull():
            return pix
    except (OSError, Exception):
        pass
    return QPixmap()


def sidebar_logo_pixmap(max_h: int = 64) -> QPixmap:
    raw = pixmap_from_png(logo_path())
    if raw.isNull():
        return raw
    return raw.scaledToHeight(max_h, Qt.SmoothTransformation)


def build_app_icon() -> QIcon:
    """High-DPI friendly icon for window + taskbar (car artwork)."""
    icon = QIcon()
    pix = pixmap_from_png(logo_path())
    if pix.isNull():
        return icon
    for size in (16, 20, 24, 32, 40, 48, 64, 96, 128, 256):
        icon.addPixmap(
            pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
    return icon


def _windows_use_custom_taskbar_icon() -> None:
    """
    Without this, the Windows taskbar often keeps the python.exe icon for scripts.
    Set an AppUserModelID so the taskbar uses this process's window icon (the car).
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "VehicleChain.BlockchainOwnership.GUI.1.0"
        )
    except Exception:
        pass


# Windows 11+ (build 22000+): native red title bar for the real window caption.
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36


def _rgb_to_colorref(rgb: int) -> int:
    """Convert 0xRRGGBB to Win32 COLORREF (0x00BBGGRR)."""
    r = (rgb >> 16) & 0xFF
    g = (rgb >> 8) & 0xFF
    b = rgb & 0xFF
    return b << 16 | g << 8 | r


def apply_native_red_titlebar(widget: QWidget, caption_rgb: int = 0xC62828, text_rgb: int = 0xFFFFFF) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        hwnd = int(widget.winId())
        dwm = ctypes.windll.dwmapi
        cap = ctypes.c_int(_rgb_to_colorref(caption_rgb))
        hr = dwm.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_CAPTION_COLOR,
            ctypes.byref(cap),
            ctypes.sizeof(cap),
        )
        if hr != 0:
            return
        txt = ctypes.c_int(_rgb_to_colorref(text_rgb))
        dwm.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_TEXT_COLOR,
            ctypes.byref(txt),
            ctypes.sizeof(txt),
        )
    except Exception:
        pass


QSS = """
QMainWindow, QWidget#root {
  background: #F0F2F5;
}
QFrame#logoFrame {
  background: #FFFFFF;
  border-radius: 20px;
  border: 1px solid #E8EAED;
}
QWidget#sidebarLogoCard {
  background: transparent;
}
QLabel#sidebarStatus {
  color: #5F6368;
  font-size: 11px;
  font-weight: 500;
  padding: 8px 12px;
  background: #FFFFFF;
  border-radius: 10px;
  border: 1px solid #DADCE0;
  margin: 6px 8px 4px 8px;
}
QWidget#sidebar {
  background: transparent;
  border: none;
}
QWidget#contentShell {
  background: #FFFFFF;
  border: 1px solid #E8EAED;
  border-radius: 20px;
}
QPushButton#nav {
  background: transparent;
  color: #3C4043;
  font-size: 13px;
  font-weight: 500;
  text-align: left;
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  margin: 2px 8px;
}
QPushButton#nav:hover {
  background: #F1F3F4;
  color: #C62828;
}
QPushButton#nav[active=true] {
  background: #C62828;
  color: #FFFFFF;
}
QWidget#card {
  background: #FFFFFF;
  border: 1px solid #E8EAED;
  border-radius: 16px;
}
QLabel#cardtitle {
  color: #C62828;
  font-size: 22px;
  font-weight: 700;
  padding: 4px 0 6px 0;
  letter-spacing: -0.3px;
}
QLabel#cardsub {
  color: #80868B;
  font-size: 13px;
  font-weight: 400;
}
QLabel#fieldlabel {
  color: #C62828;
  font-size: 12px;
  font-weight: 600;
}
QLineEdit {
  background: #FFFFFF;
  border: 1px solid #DADCE0;
  border-radius: 10px;
  color: #202124;
  font-size: 14px;
  padding: 11px 14px;
}
QLineEdit:focus {
  border: 1px solid #C62828;
  background: #FFFFFF;
}
QPushButton#action {
  background: #C62828;
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 600;
  padding: 11px 24px;
  border: none;
  border-radius: 10px;
}
QPushButton#action:hover {
  background: #B71C1C;
}
QPushButton#action:pressed {
  background: #8E0000;
}
QPushButton#action:disabled {
  background: #E8EAED;
  color: #9AA0A6;
}
QTextEdit#resultPanel {
  background: #F1F3F4;
  border: none;
  border-radius: 12px;
  padding: 14px 16px;
  color: #202124;
  font-family: "Segoe UI", "Segoe UI Symbol", sans-serif;
  font-size: 13px;
  line-height: 1.45;
}
QTableWidget#accountsTable {
  background: #FFFFFF;
  border: 1px solid #E8EAED;
  border-radius: 12px;
  gridline-color: #E8EAED;
  font-size: 13px;
  color: #202124;
  selection-background-color: #F1F3F4;
  selection-color: #202124;
}
QTableWidget#accountsTable::item {
  padding: 8px 6px;
  border: none;
}
QHeaderView::section {
  background: #F8F9FA;
  color: #5F6368;
  font-size: 11px;
  font-weight: 600;
  padding: 10px 8px;
  border: none;
  border-bottom: 1px solid #DADCE0;
}
QScrollArea {
  border: none;
  background: transparent;
}
QScrollBar:vertical {
  background: #F1F3F4;
  width: 6px;
  border-radius: 3px;
  margin: 6px 2px 6px 0;
}
QScrollBar::handle:vertical {
  background: #BDC1C6;
  border-radius: 3px;
  min-height: 24px;
}
QScrollBar::handle:vertical:hover {
  background: #9AA0A6;
}
QCheckBox {
  color: #3C4043;
  font-size: 13px;
  spacing: 8px;
}
QCheckBox::indicator {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 1px solid #C62828;
}
QCheckBox::indicator:checked {
  background: #C62828;
}
QSplitter::handle {
  background: transparent;
  width: 4px;
}
"""

def _blockchain_error_text() -> str:
    if _BLOCKCHAIN_ERROR is not None:
        return str(_BLOCKCHAIN_ERROR)
    return "Ganache is not running or is unreachable."


def _require_blockchain(box, action: str) -> bool:
    if bc is None:
        if box is not None:
            show(box, f"Error: {action} unavailable. {_blockchain_error_text()}")
        return False
    try:
        if not bc.w3.is_connected():
            msg = "Unable to connect to Ganache at http://127.0.0.1:7545. Start Ganache and try again."
            if box is not None:
                show(box, f"Error: {msg}")
            return False
    except Exception as exc:
        if box is not None:
            show(box, f"Error: {exc}")
        return False
    return True


def _require_address(box: QTextEdit, label: str, addr: str) -> bool:
    if not addr:
        show(box, f"Error: {label} is required.")
        return False
    if not Web3.is_address(addr):
        show(box, f"Error: {label} must be a valid 0x address.")
        return False
    return True


def _require_ganache_account(box: QTextEdit, label: str, addr: str) -> bool:
    """Check if address is a valid unlocked Ganache account."""
    if not _require_address(box, label, addr):
        return False
    if not bc.is_valid_ganache_account(addr):
        show(box, f"Error: {label} is not an unlocked Ganache account. Check your address.")
        return False
    return True


def _require_vehicle_id(box: QTextEdit, vehicle_id: str) -> bool:
    """Validate vehicle ID format."""
    result = validate_vehicle_id(vehicle_id)
    if not result.valid:
        show(box, f"Error: {result.message}")
        return False
    return True


def _format_error(error_str: str) -> str:
    """Extract clean error message from exception."""
    msg = str(error_str)
    if "sender account not recognized" in msg:
        return "The sender account was not recognized. Check the address."
    elif "insufficient funds" in msg.lower():
        return "Insufficient funds for gas."
    elif "revert" in msg.lower():
        return "Transaction reverted. Check your inputs and permissions."
    else:
        first_line = msg.split("\n")[0]
        return first_line[:200]


def _safe_block_number() -> str:
    try:
        if bc is not None:
            return str(bc.w3.eth.block_number)
    except Exception:
        pass
    return "—"


def ts(u):
    try: return datetime.utcfromtimestamp(u).strftime("%Y-%m-%d %H:%M:%S UTC")
    except: return str(u)

class Worker(QThread):
    result=pyqtSignal(object)
    error=pyqtSignal(str)
    def __init__(self,fn,*a,**kw): super().__init__(); self.fn=fn; self.a=a; self.kw=kw
    def run(self):
        try: self.result.emit(self.fn(*self.a,**self.kw))
        except Exception as e: self.error.emit(str(e))

def card(parent=None):
    w=QWidget(parent); w.setObjectName("card"); return w

def field(label,placeholder,parent=None):
    lbl=QLabel(label,parent); lbl.setObjectName("fieldlabel")
    e=QLineEdit(parent); e.setPlaceholderText(placeholder); return lbl,e

def result_box(parent=None,h=120):
    t = QTextEdit(parent)
    t.setObjectName("resultPanel")
    t.setReadOnly(True)
    t.setFrameStyle(QFrame.NoFrame)
    t.setFixedHeight(h)
    t.setFocusPolicy(Qt.NoFocus)
    t.setAcceptRichText(False)
    t.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    t.viewport().setCursor(Qt.ArrowCursor)
    return t

def accounts_table(parent=None, min_h=220):
    t = QTableWidget(0, 4, parent)
    t.setObjectName("accountsTable")
    t.setHorizontalHeaderLabels(["#", "Address", "Balance (ETH)", "Role"])
    t.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    t.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    t.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    t.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
    t.horizontalHeader().setStretchLastSection(False)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setSelectionMode(QAbstractItemView.NoSelection)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.setShowGrid(True)
    t.setMinimumHeight(min_h)
    t.setFrameShape(QFrame.NoFrame)
    t.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    t.setTextElideMode(Qt.ElideNone)
    return t

def show(box,text): box.setPlainText(text)
def action_btn(text,parent=None):
    b=QPushButton(text,parent); b.setObjectName("action"); return b

def scroll_wrap(widget):
    sa = QScrollArea()
    sa.setWidget(widget)
    sa.setWidgetResizable(True)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    sa.setFrameShape(QFrame.NoFrame)
    # Default QScrollArea centers a smaller child; left-align so content uses full width.
    sa.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    sa.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
    return sa

def panel_base():
    w=QWidget(); lay=QVBoxLayout(w); lay.setContentsMargins(28, 20, 28, 24); lay.setSpacing(14)
    return w,lay

def add_title(lay,title,sub=""):
    t=QLabel(title); t.setObjectName("cardtitle"); lay.addWidget(t)
    if sub: s=QLabel(sub); s.setObjectName("cardsub"); lay.addWidget(s)
    sep=QFrame(); sep.setFrameShape(QFrame.NoFrame); sep.setFixedHeight(1)
    sep.setStyleSheet("background:#E8EAED;border:none;border-radius:1px;max-height:1px;")
    lay.addWidget(sep)

def add_field(lay,label,ph,ref_dict,key):
    lb=QLabel(label); lb.setObjectName("fieldlabel"); lay.addWidget(lb)
    e=QLineEdit(); e.setPlaceholderText(ph); lay.addWidget(e); ref_dict[key]=e; return e


class DashPanel(QWidget):
    update_sig=pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        w,lay=panel_base(); add_title(lay,"Dashboard","Live Ganache network overview")
        row=QHBoxLayout()
        self.conn_card=self._stat_card("CONNECTION","—","#2E7D32")
        self.block_card=self._stat_card("LATEST BLOCK","—","#D32F2F")
        row.addWidget(self.conn_card[0]); row.addWidget(self.block_card[0]); row.addStretch()
        lay.addLayout(row)
        lay.addWidget(QLabel("Ganache Accounts", styleSheet="color:#C62828;font-size:13px;font-weight:600;margin-top:8px;"))
        self.acc_table = accounts_table(min_h=240)
        lay.addWidget(self.acc_table, 1)
        self.contract_lbl=QLabel("Contract: not deployed yet"); self.contract_lbl.setStyleSheet("color:#78909C;font-size:13px;")
        lay.addWidget(self.contract_lbl)
        b=action_btn("Refresh"); b.clicked.connect(self.refresh); lay.addWidget(b,0,Qt.AlignLeft)
        self.setLayout(QVBoxLayout())
        outer = self.layout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll_wrap(w), 1)
        self.refresh()

    def _stat_card(self,title,val,col):
        c=QWidget(); c.setObjectName("card"); c.setFixedSize(180,90)
        v=QVBoxLayout(c)
        t=QLabel(title); t.setStyleSheet("color:#757575;font-size:10px;font-weight:600;"); v.addWidget(t,0,Qt.AlignCenter)
        l=QLabel(val); l.setStyleSheet(f"color:{col};font-size:22px;font-weight:700;"); v.addWidget(l,0,Qt.AlignCenter)
        return c,l

    def refresh(self):
        try:
            if bc is None:
                raise RuntimeError(_blockchain_error_text())
            ok = bc.w3.is_connected()
            block = bc.w3.eth.block_number if ok else "—"
            self.conn_card[1].setText("Connected" if ok else "Offline")
            self.conn_card[1].setStyleSheet(f"color:{'#2E7D32' if ok else '#D32F2F'};font-size:16px;font-weight:700;")
            self.block_card[1].setText(str(block))
            if not ok:
                self.acc_table.setRowCount(0)
                self.acc_table.insertRow(0)
                self.acc_table.setItem(0, 0, QTableWidgetItem("—"))
                self.acc_table.setItem(0, 1, QTableWidgetItem("Disconnected"))
                self.acc_table.setItem(0, 2, QTableWidgetItem(""))
                self.acc_table.setItem(0, 3, QTableWidgetItem("Start Ganache to load accounts."))
                self.contract_lbl.setText("Contract: not connected")
                self.contract_lbl.setStyleSheet("color:#78909C;font-size:13px;")
                return
            auth = bc.get_authority_address().lower()
            self.acc_table.setRowCount(0)
            for i, a in enumerate(bc.w3.eth.accounts):
                wei = bc.w3.eth.get_balance(a)
                eth = float(bc.w3.from_wei(wei, "ether"))
                is_auth = a.lower() == auth
                note = "Pays deploy, register, set verifier" if is_auth else ""
                r = self.acc_table.rowCount()
                self.acc_table.insertRow(r)
                self.acc_table.setItem(r, 0, QTableWidgetItem(str(i)))
                self.acc_table.setItem(r, 1, QTableWidgetItem(a))
                bal_it = QTableWidgetItem(f"{eth:.6f}")
                bal_it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.acc_table.setItem(r, 2, bal_it)
                self.acc_table.setItem(r, 3, QTableWidgetItem(note if note else ""))
                if is_auth:
                    for c in range(4):
                        it = self.acc_table.item(r, c)
                        if it:
                            f = it.font()
                            f.setBold(True)
                            it.setFont(f)
                            it.setForeground(QBrush(QColor("#C62828")))
            try: self.contract_lbl.setText(f"Contract deployed: {bc.get_contract().address}"); self.contract_lbl.setStyleSheet("color:#2E7D32;font-size:13px;")
            except: self.contract_lbl.setText("Contract: not deployed yet"); self.contract_lbl.setStyleSheet("color:#78909C;font-size:13px;")
        except Exception as e:
            self.acc_table.setRowCount(0)
            self.acc_table.insertRow(0)
            self.acc_table.setItem(0, 0, QTableWidgetItem("—"))
            self.acc_table.setItem(0, 1, QTableWidgetItem("Error"))
            self.acc_table.setItem(0, 2, QTableWidgetItem(""))
            self.acc_table.setItem(0, 3, QTableWidgetItem(str(e)))


class DeployPanel(QWidget):
    def __init__(self):
        super().__init__()
        w,lay=panel_base(); add_title(lay,"Deploy Contract","Compile VehicleOwnership.sol and deploy to Ganache")
        self.out=result_box(h=220); show(self.out,"Click Deploy to compile and deploy the smart contract.")
        lay.addWidget(self.out)
        b=action_btn("Deploy Contract"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        if not _require_blockchain(self.out, "Deploy Contract"):
            return
        show(self.out,"Compiling Solidity contract… please wait."); QApplication.processEvents()
        def fn(): return bc.deploy_contract()
        self._w=Worker(fn); self._w.result.connect(self.done); self._w.error.connect(lambda e: show(self.out,f"Error: {e}")); self._w.start()

    def done(self,result):
        addr, tx_hash = result
        log_action("DEPLOY",tx_hash=tx_hash,notes=f"Contract at {addr}")
        block = "—"
        deployer = "—"
        try:
            if bc is not None:
                block = bc.w3.eth.block_number
                deployer = bc.w3.eth.accounts[0]
        except Exception:
            pass
        show(self.out,f"Smart contract deployed.\n\n  Address  : {addr}\n  Block    : #{block}\n  Chain ID : 1337\n  Deployer : {deployer}\n\n  The authority is now locked — access control is active.\n  Next: Register Vehicle")


class RegisterPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"Register Vehicle","Only the authority can register vehicles — each Vehicle ID is unique on-chain")
        reg_hint=QLabel(
            "Gas is paid by the authority wallet (highlighted on the Dashboard), not by the Owner address. "
            "Fees are small; click Refresh on the Dashboard after registering to see the ETH balance change."
        )
        reg_hint.setWordWrap(True)
        reg_hint.setStyleSheet("color:#80868B;font-size:12px;margin-bottom:4px;")
        lay.addWidget(reg_hint)
        for k,l,p in [("vid","Vehicle ID","17-char VIN or custom ID e.g. CAR001"),
                      ("brand","Brand","e.g. Toyota"),("model","Model","e.g. Corolla"),
                      ("owner","Owner Address","0x…wallet address")]:
            add_field(lay,l,p,self.fields,k)
        self.badge=QLabel(""); self.badge.setStyleSheet("font-size:12px;margin:2px 0;"); lay.addWidget(self.badge)
        self.fields["vid"].textChanged.connect(self.vid_changed)
        self.out=result_box(h=140); lay.addWidget(self.out)
        b=action_btn("Register Vehicle"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def vid_changed(self,txt):
        r=validate_vehicle_id(txt)
        col={"VIN":"#2E7D32","CUSTOM":"#D32F2F","EMPTY":"#757575"}.get(r.mode,"#D32F2F")
        if not r.valid: col="#D32F2F"
        self.badge.setText(f"{r.message}  {r.detail}" if r.detail else r.message)
        self.badge.setStyleSheet(f"color:{col};font-size:12px;")

    def go(self):
        if not _require_blockchain(self.out, "Register Vehicle"):
            return
        vid=self.fields["vid"].text().strip(); brand=self.fields["brand"].text().strip()
        model=self.fields["model"].text().strip(); owner=self.fields["owner"].text().strip()
        r=validate_vehicle_id(vid)
        if not r.valid: show(self.out,f"Error: {r.message}"); return
        if not all([brand,model,owner]): show(self.out,"All fields required."); return
        if not _require_ganache_account(self.out, "Owner address", owner): return
        show(self.out,"Sending transaction…"); QApplication.processEvents()
        def fn(): return bc.register_vehicle(vid,brand,model,owner)
        self._w=Worker(fn)
        self._w.result.connect(lambda tx: (log_action("REGISTER",vid,owner,str(tx),_safe_block_number()),
            show(self.out,f"Vehicle registered.\n\n  Vehicle ID  : {vid}  [{r.mode}]\n  Brand/Model : {brand} {model}\n  Owner       : {owner}\n  TX Hash     : {tx}\n  Block #     : {_safe_block_number()}\n\n  This record is permanently immutable on the blockchain.")))
        self._w.error.connect(lambda e: show(self.out,f"Error: {_format_error(e)}")); self._w.start()


class TransferPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"Transfer Ownership","Only the current owner can transfer — each transfer is an immutable blockchain transaction")
        for k,l,p in [("vid","Vehicle ID","e.g. CAR001"),("cur","Current Owner Address","0x…"),("new","New Owner Address","0x…")]:
            add_field(lay,l,p,self.fields,k)
        self.out=result_box(h=150); lay.addWidget(self.out)
        b=action_btn("Transfer Ownership"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        if not _require_blockchain(self.out, "Transfer Ownership"):
            return
        vid=self.fields["vid"].text().strip(); cur=self.fields["cur"].text().strip(); new_=self.fields["new"].text().strip()
        if not all([vid,cur,new_]): show(self.out,"All fields required."); return
        if not _require_ganache_account(self.out, "Current owner address", cur): return
        if not _require_ganache_account(self.out, "New owner address", new_): return
        if cur.lower() == new_.lower(): show(self.out,"Error: New owner must be different from current owner."); return
        show(self.out,"Sending transaction…"); QApplication.processEvents()
        def fn(): return bc.transfer_ownership(vid,new_,current_owner_address=cur)
        self._w=Worker(fn)
        self._w.result.connect(lambda tx: (log_action("TRANSFER",vid,cur,str(tx),_safe_block_number(),f"to {new_}"),
            show(self.out,f"Ownership transferred.\n\n  Vehicle ID    : {vid}\n  Previous Owner: {cur}\n  New Owner     : {new_}\n  TX Hash       : {tx}\n  Block #       : {_safe_block_number()}\n\n  This transfer is permanently recorded and cannot be reversed.")))
        self._w.error.connect(lambda e: show(self.out,f"Error: {_format_error(e)}")); self._w.start()


class VerifyPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"Verify Owner","Anyone can verify the current owner — no login required")
        add_field(lay,"Vehicle ID","e.g. CAR001",self.fields,"vid")
        self.out=result_box(h=90); lay.addWidget(self.out)
        b=action_btn("Verify Owner"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        vid=self.fields["vid"].text().strip()
        if not vid: show(self.out,"Enter a vehicle ID."); return
        if not _require_blockchain(self.out, "Verify Owner"):
            return
        def fn(): return bc.verify_owner(vid)
        self._w=Worker(fn)
        self._w.result.connect(lambda o: (log_action("VERIFY",vid,notes=f"Owner={o}"), show(self.out,f"Current owner of '{vid}':\n\n  {o}")))
        self._w.error.connect(lambda e: show(self.out,f"Error: {e}")); self._w.start()


class DetailsPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"Vehicle Details","Full on-chain vehicle record — ID, brand, model, owner, registration timestamp")
        add_field(lay,"Vehicle ID","e.g. CAR001",self.fields,"vid")
        self.out=result_box(h=180); lay.addWidget(self.out)
        b=action_btn("Fetch Details"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        vid=self.fields["vid"].text().strip()
        if not vid: show(self.out,"Enter a vehicle ID."); return
        if not _require_blockchain(self.out, "Fetch Details"):
            return
        def fn(): return bc.get_vehicle(vid)
        self._w=Worker(fn)
        self._w.result.connect(lambda v: show(self.out,
            f"  Vehicle ID   :  {v['vehicle_id']}\n  Brand        :  {v['brand']}\n  Model        :  {v['model']}\n  Owner        :  {v['current_owner']}\n  Registered   :  {ts(v['registered_at'])}"))
        self._w.error.connect(lambda e: show(self.out,f"Error: {e}")); self._w.start()


class HistoryPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"Ownership History","Full traceable ownership chain — every transfer permanently stored on-chain")
        add_field(lay,"Vehicle ID","e.g. CAR001",self.fields,"vid")
        self.out=result_box(h=300); lay.addWidget(self.out)
        b=action_btn("Fetch History"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        vid=self.fields["vid"].text().strip()
        if not vid: show(self.out,"Enter a vehicle ID."); return
        if not _require_blockchain(self.out, "Fetch History"):
            return
        def fn(): return bc.get_history(vid)
        self._w=Worker(fn)
        def display(recs):
            if not recs: show(self.out,"No history found."); return
            lines=[f"History for '{vid}'  —  {len(recs)} record(s)\n"+"─"*55]
            for i,r in enumerate(recs):
                ev="REGISTERED" if i==0 else "TRANSFERRED"
                lines+=[f"\n[{i+1}]  {ev}",f"     Address  :  {r['owner']}",f"     Time     :  {ts(r['transferred_at'])}"]
            show(self.out,"\n".join(lines))
        self._w.result.connect(display); self._w.error.connect(lambda e: show(self.out,f"Error: {e}")); self._w.start()


class CertPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"PDF Certificate","Generate a printable blockchain-verified certificate with QR code")
        add_field(lay,"Vehicle ID","e.g. CAR001",self.fields,"vid")
        self.out=result_box(h=90); lay.addWidget(self.out)
        b=action_btn("Generate PDF"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        vid=self.fields["vid"].text().strip()
        if not vid: show(self.out,"Enter a vehicle ID."); return
        if not _require_blockchain(self.out, "Generate PDF"):
            return
        show(self.out,"Generating PDF…"); QApplication.processEvents()
        def fn():
            from vehiclechain.pdf_cert import generate_certificate

            return generate_certificate(vid)
        self._w=Worker(fn)
        def done(path): show(self.out,f"Certificate saved.\n\n  {path}"); os.startfile(path)
        self._w.result.connect(done); self._w.error.connect(lambda e: show(self.out,f"Error: {e}")); self._w.start()


class AuditPanel(QWidget):
    def __init__(self):
        super().__init__()
        w,lay=panel_base(); add_title(lay,"Audit Log","Every action is automatically logged with timestamp, TX hash, and block number")
        self.out=result_box(h=340); lay.addWidget(self.out)
        row=QHBoxLayout()
        b1=action_btn("Refresh"); b1.clicked.connect(self.load); row.addWidget(b1)
        b2=action_btn("Open CSV"); b2.clicked.connect(lambda: os.startfile(get_log_path()) if os.path.exists(get_log_path()) else None)
        row.addWidget(b2); row.addStretch(); lay.addLayout(row)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def load(self):
        rows=read_log()
        if not rows: show(self.out,"No audit records yet."); return
        hdr=f"{'TIMESTAMP':<22} {'ACTION':<14} {'VEHICLE ID':<20} TX HASH\n"+"─"*80
        lines=[hdr]+[f"{r['timestamp']:<22} {r['action']:<14} {r['vehicle_id']:<20} {r['tx_hash'][:18]}…" for r in rows]
        show(self.out,"\n".join(lines))


class VerifierPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"Set Verifier","Authority can grant or revoke the official verifier badge for trusted inspectors")
        info=QWidget(); info.setObjectName("card"); iv=QVBoxLayout(info)
        t=QLabel("What is a Verifier?"); t.setStyleSheet("color:#C62828;font-size:14px;font-weight:700;"); iv.addWidget(t)
        d=QLabel("A verifier is an officially authorized inspector (e.g. insurance company, police, DMV).\nTheir wallet address is stored on-chain in the verifiers mapping — publicly readable.\nThird-party systems can call verifiers[address] to confirm official authorization.\nRoles: Authority (register/manage)  ·  Owner (transfer)  ·  Verifier (trusted badge).")
        d.setStyleSheet("color:#78909C;font-size:13px;"); d.setWordWrap(True); iv.addWidget(d); lay.addWidget(info)
        add_field(lay,"Wallet Address","0x… address to grant or revoke",self.fields,"addr")
        self.chk=QCheckBox("Grant Access"); self.chk.setChecked(True); self.chk.setStyleSheet("color:#3C4043;font-size:13px;padding:4px 0;")
        lay.addWidget(self.chk)
        self.out=result_box(h=100); lay.addWidget(self.out)
        b=action_btn("Apply"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        addr=self.fields["addr"].text().strip(); allowed=self.chk.isChecked()
        if not addr: show(self.out,"Enter a wallet address."); return
        if not _require_blockchain(self.out, "Set Verifier"):
            return
        if not _require_address(self.out, "Verifier address", addr): return
        def fn(): return bc.set_verifier(addr,allowed)
        self._w=Worker(fn)
        def done(tx):
            act="GRANTED" if allowed else "REVOKED"; log_action("SET_VERIFIER",tx_hash=tx,notes=f"{act} {addr}")
            show(self.out,f"Verifier {act}.\n\n  Address : {addr}\n  TX Hash : {tx}\n  Block # : {_safe_block_number()}")
        self._w.result.connect(done); self._w.error.connect(lambda e: show(self.out,f"Error: {_format_error(e)}")); self._w.start()


class VerifierConfirmPanel(QWidget):
    def __init__(self):
        super().__init__(); self.fields={}
        w,lay=panel_base(); add_title(lay,"Verifier Confirmation","Authorized verifiers can create audit trails by confirming vehicle ownership")
        info=QWidget(); info.setObjectName("card"); iv=QVBoxLayout(info)
        t=QLabel("Create Audit Trail"); t.setStyleSheet("color:#C62828;font-size:14px;font-weight:700;"); iv.addWidget(t)
        d=QLabel("Only authorized verifiers can call this function.\nIt creates an immutable OwnershipVerified event on the blockchain.\nThe current owner address and timestamp are permanently recorded.\nThis provides transparent proof of verification for third-party systems.")
        d.setStyleSheet("color:#78909C;font-size:13px;"); d.setWordWrap(True); iv.addWidget(d); lay.addWidget(info)
        add_field(lay,"Vehicle ID","e.g. CAR001",self.fields,"vid")
        add_field(lay,"Your Verifier Address","0x… wallet address",self.fields,"addr")
        self.out=result_box(h=120); lay.addWidget(self.out)
        b=action_btn("Confirm Ownership"); b.clicked.connect(self.go); lay.addWidget(b,0,Qt.AlignLeft)
        lay.addStretch(); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_wrap(w))

    def go(self):
        vid=self.fields["vid"].text().strip(); addr=self.fields["addr"].text().strip()
        if not vid: show(self.out,"Enter a vehicle ID."); return
        if not addr: show(self.out,"Enter your verifier address."); return
        if not _require_blockchain(self.out, "Verify Ownership"):
            return
        if not _require_vehicle_id(self.out, vid): return
        if not _require_ganache_account(self.out, "Verifier address", addr): return
        def fn(): return bc.verify_ownership_by_verifier(vid,addr)
        self._w=Worker(fn)
        def done(result):
            owner, tx_hash = result
            log_action("VERIFIER_CONFIRM",vid,tx_hash=tx_hash,notes=f"Verifier={addr}, Owner={owner}")
            show(self.out,f"✓ Verification confirmed and recorded.\n\n  Vehicle ID : {vid}\n  Owner      : {owner}\n  Verifier   : {addr}\n  TX Hash    : {tx_hash[:16]}…\n  Block #    : {_safe_block_number()}")
        self._w.result.connect(done); self._w.error.connect(lambda e: show(self.out,f"Error: {_format_error(e)}")); self._w.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VehicleChain — Blockchain Ownership System")
        self.resize(1200,760)
        self.setStyleSheet(QSS)

        root=QWidget(); root.setObjectName("root"); self.setCentralWidget(root)
        main_lay=QVBoxLayout(root); main_lay.setContentsMargins(0,0,0,0); main_lay.setSpacing(0)

        shell_wrap=QWidget()
        shell_lay=QHBoxLayout(shell_wrap)
        shell_lay.setContentsMargins(20, 18, 20, 18)
        shell_lay.setSpacing(0)

        body=QSplitter(Qt.Horizontal); body.setHandleWidth(0)

        sb=QWidget(); sb.setObjectName("sidebar"); sb.setFixedWidth(208)
        sbl=QVBoxLayout(sb); sbl.setContentsMargins(0, 4, 12, 8); sbl.setSpacing(4)

        logo_card=QWidget()
        logo_card.setObjectName("sidebarLogoCard")
        logo_outer=QVBoxLayout(logo_card)
        logo_outer.setContentsMargins(8, 8, 8, 16)
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_frame.setFrameShape(QFrame.NoFrame)
        logo_lay = QVBoxLayout(logo_frame)
        logo_lay.setContentsMargins(14, 14, 14, 14)
        logo_mark = QLabel()
        logo_mark.setAlignment(Qt.AlignCenter)
        # Plain QLabel (no QSS object name): Qt can fail to paint pixmaps on styleshe QLabel on Windows.
        _pm = sidebar_logo_pixmap(64)
        if not _pm.isNull():
            logo_mark.setPixmap(_pm)
            logo_mark.setMinimumHeight(64)
        else:
            logo_mark.setText("VehicleChain")
            logo_mark.setStyleSheet("color:#C62828;font-size:12px;font-weight:700;")
        logo_lay.addWidget(logo_mark)
        logo_outer.addWidget(logo_frame)
        sbl.addWidget(logo_card)

        self.stack=QStackedWidget()
        panels=[
            ("Dashboard",          DashPanel()),
            ("Deploy Contract",    DeployPanel()),
            ("Register Vehicle",   RegisterPanel()),
            ("Transfer Ownership", TransferPanel()),
            ("Verify Owner",       VerifyPanel()),
            ("Vehicle Details",    DetailsPanel()),
            ("Ownership History",  HistoryPanel()),
            ("PDF Certificate",    CertPanel()),
            ("Audit Log",          AuditPanel()),
            ("Set Verifier",       VerifierPanel()),
            ("Verifier Confirmation", VerifierConfirmPanel()),
        ]
        self._nav=[]
        for i,(label,panel) in enumerate(panels):
            self.stack.addWidget(panel)
            b=QPushButton(label); b.setObjectName("nav"); b.setCheckable(False)
            b.clicked.connect(lambda _,idx=i: self._switch(idx))
            sbl.addWidget(b); self._nav.append(b)
        sbl.addStretch()
        self.status_lbl=QLabel("Connecting…")
        self.status_lbl.setObjectName("sidebarStatus")
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setStyleSheet(
            "color:#5F6368;font-size:11px;font-weight:500;padding:8px 12px;"
            "background:#FFFFFF;border-radius:10px;border:1px solid #DADCE0;"
            "margin:6px 8px 4px 8px;"
        )
        sbl.addWidget(self.status_lbl)

        content_shell=QWidget()
        content_shell.setObjectName("contentShell")
        csl=QVBoxLayout(content_shell)
        csl.setContentsMargins(20, 18, 20, 18)
        csl.addWidget(self.stack)

        body.addWidget(sb); body.addWidget(content_shell)
        body.setStretchFactor(1, 1)
        shell_lay.addWidget(body)
        main_lay.addWidget(shell_wrap, 1)
        self._switch(0)
        self._start_poll()

        ic = build_app_icon()
        if not ic.isNull():
            self.setWindowIcon(ic)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, lambda: apply_native_red_titlebar(self))

    def _switch(self,idx):
        self.stack.setCurrentIndex(idx)
        for i,b in enumerate(self._nav):
            b.setProperty("active","true" if i==idx else "false")
            b.style().unpolish(b); b.style().polish(b)

    def _start_poll(self):
        def run():
            while True:
                try:
                    if bc is None:
                        self.status_lbl.setText("Blockchain unavailable")
                        self.status_lbl.setStyleSheet(
                            "color:#C5221F;font-size:11px;font-weight:500;padding:8px 12px;"
                            "background:#FFFFFF;border-radius:10px;border:1px solid #FAD2CF;"
                            "margin:6px 8px 4px 8px;"
                        )
                    else:
                        ok = bc.w3.is_connected()
                        block = bc.w3.eth.block_number if ok else "—"
                        if ok:
                            self.status_lbl.setText(f"Connected, block #{block}")
                            self.status_lbl.setStyleSheet(
                                "color:#137333;font-size:11px;font-weight:500;padding:8px 12px;"
                                "background:#FFFFFF;border-radius:10px;border:1px solid #CEEAD6;"
                                "margin:6px 8px 4px 8px;"
                            )
                        else:
                            self.status_lbl.setText("Disconnected from Ganache")
                            self.status_lbl.setStyleSheet(
                                "color:#C5221F;font-size:11px;font-weight:500;padding:8px 12px;"
                                "background:#FFFFFF;border-radius:10px;border:1px solid #FAD2CF;"
                                "margin:6px 8px 4px 8px;"
                            )
                except Exception:
                    self.status_lbl.setText("Network error")
                    self.status_lbl.setStyleSheet(
                        "color:#B3261E;font-size:11px;font-weight:500;padding:8px 12px;"
                        "background:#FFFFFF;border-radius:10px;border:1px solid #FAD2CF;"
                        "margin:6px 8px 4px 8px;"
                    )
                time.sleep(3)
        threading.Thread(target=run,daemon=True).start()


def run() -> int:
    _windows_use_custom_taskbar_icon()
    app = QApplication(sys.argv)
    app.setApplicationName("VehicleChain")
    app.setApplicationDisplayName("VehicleChain")
    app.setFont(QFont("Segoe UI", 13))
    _icon = build_app_icon()
    if not _icon.isNull():
        app.setWindowIcon(_icon)
    w = MainWindow()
    if not _icon.isNull():
        w.setWindowIcon(_icon)
    w.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run())
