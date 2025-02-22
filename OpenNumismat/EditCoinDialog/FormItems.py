# -*- coding: utf-8 -*-

import locale
import re

from PyQt5.QtCore import QMargins, QUrl, QDate, Qt, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from OpenNumismat.Collection.CollectionFields import Statuses
from OpenNumismat.Settings import Settings
from OpenNumismat.Tools.Gui import statusIcon
from OpenNumismat.Tools.Converters import numberWithFraction, htmlToPlainText


# Reimplementing QDoubleValidator for replace comma with dot
class DoubleValidator(QDoubleValidator):
    def __init__(self, bottom, top, decimals, parent=None):
        super().__init__(bottom, top, decimals, parent)
        self.setNotation(QDoubleValidator.StandardNotation)

    def validate(self, input_, pos):
        input_ = input_.lstrip()
        if len(input_) == 0:
            return QValidator.Intermediate, input_, pos

        lastWasDigit = False
        decPointFound = False
        decDigitCnt = 0
        value = '0'
        ts = [locale.localeconv()['thousands_sep'], ]
        if ts[0] == chr(0xA0):
            ts.append(' ')
        dp = [locale.localeconv()['decimal_point'], ]
        if dp[0] == ',' and '.' not in ts:
            dp.append('.')

        for c in input_:
            if c.isdigit():
                if decPointFound and self.decimals() > 0:
                    if decDigitCnt < self.decimals():
                        decDigitCnt += 1
                    else:
                        return QValidator.Invalid, input_, pos

                value = value + c
                lastWasDigit = True
            else:
                if c in dp and self.decimals() != 0:
                    if decPointFound:
                        return QValidator.Invalid, input_, pos
                    else:
                        value += '.'
                        decPointFound = True
                elif c in ts:
                    if not lastWasDigit or decPointFound:
                        return QValidator.Invalid, input_, pos
                elif c == '-' and value == '0':
                    if self.bottom() > 0:
                        return QValidator.Invalid, input_, pos
                    value = '-0'
                else:
                    return QValidator.Invalid, input_, pos

                lastWasDigit = False

        try:
            val = float(value)
        except ValueError:
            return QValidator.Invalid, input_, pos

        if self.bottom() > val or val > self.top():
            return QValidator.Invalid, input_, pos

        return QValidator.Acceptable, input_, pos


# Reimplementing QDoubleValidator for replace thousands separators
class BigIntValidator(QDoubleValidator):
    def __init__(self, bottom, top, parent=None):
        super().__init__(bottom, top, 0, parent)

    def validate(self, input_, pos):
        input_ = input_.lstrip()
        if len(input_) == 0:
            return QValidator.Intermediate, input_, pos

        lastWasDigit = False
        value = '0'
        ts = [locale.localeconv()['thousands_sep'], ]
        if ts[0] == chr(0xA0):
            ts.append(' ')
        tss = (ts[0], ' ', chr(0xA0), '.', ',')

        for c in input_:
            if c.isdigit():
                value = value + c
                lastWasDigit = True
            else:
                if c in tss:
                    if not lastWasDigit:
                        return QValidator.Invalid, input_, pos
                else:
                    return QValidator.Invalid, input_, pos

                lastWasDigit = False

        try:
            val = int(value)
        except ValueError:
            return QValidator.Invalid, input_, pos

        if not lastWasDigit and len(input_) > 0 and input_[-1] not in ts:
            return QValidator.Invalid, input_, pos

        if self.bottom() > val or val > self.top():
            return QValidator.Invalid, input_, pos

        return QValidator.Acceptable, input_, pos


class NumberValidator(QIntValidator):
    def validate(self, input_, pos):
        input_ = input_.strip()
        if len(input_) == 0:
            return QValidator.Intermediate, input_, pos

        try:
            val = int(input_)
        except ValueError:
            return QValidator.Invalid, input_, pos

        if self.bottom() > val or val > self.top():
            return QValidator.Invalid, input_, pos

        return QValidator.Acceptable, input_, pos


class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(1024)
        self.setMinimumWidth(100)


class UrlLineEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.lineEdit = LineEdit(self)

        buttonLoad = QPushButton(QIcon(':/world.png'), '', self)
        buttonLoad.setFixedWidth(25)
        buttonLoad.setToolTip(self.tr("Open specified URL"))
        buttonLoad.clicked.connect(self.clickedButtonLoad)

        style = QApplication.style()
        icon = style.standardIcon(QStyle.SP_DialogOpenButton)

        self.buttonOpen = QPushButton(icon, '', parent)
        self.buttonOpen.setFixedWidth(25)
        self.buttonOpen.setToolTip(self.tr("Select file from disc"))
        self.buttonOpen.clicked.connect(self.clickedButtonOpen)

        layout = QHBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.buttonOpen)
        layout.addWidget(buttonLoad)
        layout.setContentsMargins(QMargins())

        self.setLayout(layout)

    def clickedButtonOpen(self):
        file, _selectedFilter = QFileDialog.getOpenFileName(
            self, self.tr("Select file"), self.text(), "*.*")
        if file:
            self.setText(file)

    def clickedButtonLoad(self):
        url = QUrl(self.text())

        executor = QDesktopServices()
        executor.openUrl(url)

    def clear(self):
        self.lineEdit.clear()

    def setText(self, text):
        self.lineEdit.setText(text)

    def text(self):
        return self.lineEdit.text().replace('\\', '/')

    def home(self, mark):
        self.lineEdit.home(mark)

    def setReadOnly(self, b):
        self.lineEdit.setReadOnly(b)

        if b:
            self.buttonOpen.hide()
        else:
            self.buttonOpen.show()


class AddressLineEdit(QWidget):
    findClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.lineEdit = LineEdit(self)
        self.lineEdit.returnPressed.connect(self.clickedButtonAddress)

        self.buttonAddress = QPushButton(QIcon(':/find.png'), '', self)
        self.buttonAddress.setFixedWidth(25)
        self.buttonAddress.setToolTip(self.tr("Find address"))
        self.buttonAddress.clicked.connect(self.clickedButtonAddress)

        layout = QHBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.buttonAddress)
        layout.setContentsMargins(QMargins())

        self.setLayout(layout)

    def clickedButtonAddress(self):
        text = self.text().strip()
        if text:
            self.findClicked.emit(text)

    def clear(self):
        self.lineEdit.clear()

    def setText(self, text):
        self.lineEdit.setText(text)

    def text(self):
        return self.lineEdit.text()

    def home(self, mark):
        self.lineEdit.home(mark)

    def setReadOnly(self, b):
        self.lineEdit.setReadOnly(b)

        if b:
            self.buttonAddress.hide()
        else:
            self.buttonAddress.show()


class GraderLineEdit(QWidget):
    clickedButton = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.lineEdit = LineEdit(self)

        buttonLoad = QPushButton(QIcon(':/world.png'), '', self)
        buttonLoad.setFixedWidth(25)
        buttonLoad.setToolTip(self.tr("View on grader site"))
        buttonLoad.clicked.connect(self.clickedButton)

        layout = QHBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(buttonLoad)
        layout.setContentsMargins(QMargins())

        self.setLayout(layout)

    def clear(self):
        self.lineEdit.clear()

    def setText(self, text):
        self.lineEdit.setText(text)

    def text(self):
        return self.lineEdit.text()

    def home(self, mark):
        self.lineEdit.home(mark)

    def setReadOnly(self, b):
        self.lineEdit.setReadOnly(b)

    def addAction(self, icon, position):
        return self.lineEdit.addAction(icon, position)
    
    def actions(self):
        return self.lineEdit.actions()
    
    def removeAction(self, act):
        return self.lineEdit.removeAction(act)


class LineEditRef(QWidget):
    def __init__(self, reference, parent=None):
        super().__init__(parent)

        self.comboBox = QComboBox(self)
        self.comboBox.setEditable(True)
        self.comboBox.lineEdit().setMaxLength(1024)
        self.comboBox.setMinimumWidth(120)
        self.comboBox.setInsertPolicy(QComboBox.NoInsert)

        self.model = reference.model
        self.proxyModel = self.model.proxyModel()
        self.comboBox.setModel(self.proxyModel)
        self.comboBox.setModelColumn(self.model.fieldIndex('value'))

        self.comboBox.setCurrentIndex(-1)

        self.reference = reference
        self.reference.changed.connect(self.setText)

        layout = QHBoxLayout()
        layout.addWidget(self.comboBox)
        layout.addWidget(reference.button(self))
        layout.setContentsMargins(QMargins())

        self.setLayout(layout)

        self.dependents = []

    def clear(self):
        self.comboBox.setCurrentIndex(-1)

    def setText(self, text):
        index = self.comboBox.findText(text)
        if index >= 0:
            self.comboBox.setCurrentIndex(index)
        else:
            self.comboBox.setCurrentIndex(-1)
            self.comboBox.lineEdit().setText(text)
            self.comboBox.lineEdit().setCursorPosition(0)

    def text(self):
        return self.comboBox.currentText()

    def home(self, mark):
        self.comboBox.lineEdit().home(mark)

    def addDependent(self, reference):
        # Clear reference
        reference.reference.model.setFilter(None)
        reference.reference.parentIndex = None

        if not self.dependents:
            # TODO: For support nonunique values uncomment next line
            # self.comboBox.currentIndexChanged.connect(self.updateDependents)
            self.comboBox.editTextChanged.connect(self.updateDependents)
        self.dependents.append(reference)

    def updateDependents(self, index):
        if isinstance(index, str):
            index = self.comboBox.findText(index)

        if index >= 0:
            idIndex = self.model.fieldIndex('id')
            parentIndex = self.proxyModel.index(index, idIndex)
            parent_id = parentIndex.data()
            if parent_id:
                for dependent in self.dependents:
                    text = dependent.text()
                    reference = dependent.reference
                    reference.model.setFilter(
                        '%s.parentid=%d' % (reference.model.tableName(), parent_id))
                    reference.parentIndex = parentIndex
                    dependent.setText(text)
        else:
            for dependent in self.dependents:
                text = dependent.text()
                reference = dependent.reference
                if self.comboBox.currentText():
                    reference.model.setFilter('0')  # nothing select
                else:
                    reference.model.setFilter(None)  # select all
                reference.parentIndex = None
                dependent.setText(text)


class StatusEdit(QComboBox):

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(100)

        for status, statusTitle in Statuses.items():
            if settings[status + '_status_used']:
                self.addItem(statusIcon(status), statusTitle, status)

    def data(self):
        return self.currentData()

    def clear(self):
        self.setCurrentIndex(-1)

    def setCurrentValue(self, value):
        old_index = self.currentIndex()
        index = self.findData(value)
        self.setCurrentIndex(index)
        if old_index == index:
            self.currentIndexChanged.emit(index)


class StatusBrowser(QLineEdit):
    currentIndexChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(100)
        self.data = ''

    def setCurrentValue(self, value):
        self.setText(Statuses[value])
        self.home(False)

        for act in self.actions():
            self.removeAction(act)
        icon = statusIcon(value)
        self.action = self.addAction(icon, QLineEdit.LeadingPosition)

        self.data = value

        self.currentIndexChanged.emit(-1)

    def currentData(self):
        return self.data


class ShortLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(10)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def sizeHint(self):
        return self.minimumSizeHint()


class UserNumericEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(25)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Fixed, QSizePolicy.SpinBox))

    def sizeHint(self):
        return self.minimumSizeHint()


class NumberEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        validator = NumberValidator(0, 9999, parent)
        self.setValidator(validator)
        self.setMaxLength(4)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Fixed, QSizePolicy.SpinBox))

    def sizeHint(self):
        return self.minimumSizeHint()


class YearEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.numberEdit = NumberEdit(parent)

        self.bcBtn = QCheckBox(self.tr("BC"))
        self.bcBtn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.bcLbl = QLabel()
        self.bcLbl.hide()

        layout = QHBoxLayout()
        layout.addWidget(self.numberEdit)
        layout.addWidget(self.bcBtn)
        layout.addWidget(self.bcLbl)
        layout.setContentsMargins(QMargins())

        self.setLayout(layout)

    def clear(self):
        self.numberEdit.clear()
        self.bcBtn.setCheckState(Qt.Unchecked)

    def setText(self, text):
        if text and text[0] == '-':
            text = text[1:]
            self.bcBtn.setChecked(True)
            self.bcLbl.setText(self.tr("BC"))
        else:
            self.bcLbl.clear()
        self.numberEdit.setText(text)

    def text(self):
        text = self.numberEdit.text()
        if text and self.bcBtn.isChecked():
            text = '-' + text

        return text

    def home(self, mark):
        self.numberEdit.home(mark)

    def setReadOnly(self, b):
        self.numberEdit.setReadOnly(b)

        if b:
            self.bcBtn.hide()
            self.bcLbl.show()
        else:
            self.bcBtn.show()
            self.bcLbl.hide()


class _DoubleEdit(QLineEdit):
    def __init__(self, bottom, top, decimals, parent=None):
        super().__init__(parent)
        self._decimals = decimals

        validator = DoubleValidator(bottom, top, decimals, parent)
        self.setValidator(validator)

    def focusInEvent(self, event):
        self._updateText()
        return super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._updateText()
        return super().focusOutEvent(event)

    def setText(self, text):
        ts = locale.localeconv()['thousands_sep']
        if ts == '.':
            text = text.replace('.', ',')
        super().setText(text)
        self._updateText()

    def text(self):
        text = super().text()
        # First, get rid of the grouping
        ts = locale.localeconv()['thousands_sep']
        if ts:
            text = text.replace(ts, '')
            if ts == chr(0xA0):
                text = text.replace(' ', '')
        # next, replace the decimal point with a dot
        if self._decimals:
            dp = locale.localeconv()['decimal_point']
            if dp:
                text = text.replace(dp, '.')
        return text

    def _updateText(self):
        text = self.text()
        if text:
            src_text = text

            if not self.hasFocus() or self.isReadOnly():
                try:
                    if self._decimals:
                        text = locale.format_string("%%.%df" % self._decimals,
                                             float(text), grouping=True)
                    else:
                        text = locale.format_string("%d", int(text), grouping=True)
                except ValueError:
                    return

                if self._decimals:
                    # Strip empty fraction
                    dp = locale.localeconv()['decimal_point']
                    text = text.rstrip('0').rstrip(dp)
            else:
                ts = locale.localeconv()['thousands_sep']
                if ts == '.':
                    text = text.replace('.', ',')

            if src_text != text:
                super().setText(text)


class BigIntEdit(_DoubleEdit):
    def __init__(self, parent=None):
        super().__init__(0, 999999999999999, 0, parent)

        validator = BigIntValidator(0, 999999999999999, parent)
        self.setValidator(validator)

        self.setMaxLength(15 + 4)  # additional 4 symbol for thousands separator
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Fixed, QSizePolicy.SpinBox))

    def text(self):
        text = super().text()
        ts = (locale.localeconv()['thousands_sep'], ' ', chr(0xA0), '.', ',')
        for c in ts:
            text = text.replace(c, '')
        return text


class ValueEdit(_DoubleEdit):
    def __init__(self, parent=None):
        super().__init__(0, 9999999999, 3, parent)
        self.setMaxLength(17)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Fixed, QSizePolicy.SpinBox))

    def sizeHint(self):
        return self.minimumSizeHint()


class CoordEdit(_DoubleEdit):
    def __init__(self, parent=None):
        super().__init__(-180, 180, 4, parent)
        self.setMaxLength(9)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Fixed, QSizePolicy.SpinBox))

    def sizeHint(self):
        return self.minimumSizeHint()


class MoneyEdit(_DoubleEdit):
    def __init__(self, parent=None):
        super().__init__(0, 9999999999, 2, parent)
        self.setMaxLength(16)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Fixed, QSizePolicy.SpinBox))

    def sizeHint(self):
        return self.minimumSizeHint()


class DenominationEdit(MoneyEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()

    def text(self):
        text = super().text()
        if text == '¼':
            text = '0.25'
        elif text == '⅓':
            text = '0.33'
        elif text == '½':
            text = '0.5'
        elif text == '¾':
            text = '0.75'
        elif text == '1¼':
            text = '1.25'
        elif text == '1½':
            text = '1.5'
        elif text == '2½':
            text = '2.5'
        return text

    def _updateText(self):
        text = self.text()
        if text:
            if not self.hasFocus() or self.isReadOnly():
                text, converted = numberWithFraction(text)
                if not converted:
                    try:
                        if self._decimals:
                            text = locale.format_string("%%.%df" % self._decimals,
                                                 float(text), grouping=True)
                            # Strip empty fraction
                            dp = locale.localeconv()['decimal_point']
                            text = text.rstrip('0').rstrip(dp)
                        else:
                            text = locale.format_string("%d", int(text), grouping=True)
                    except ValueError:
                        return
            else:
                ts = locale.localeconv()['thousands_sep']
                if ts == '.':
                    text = text.replace('.', ',')

            if QLineEdit.text(self) != text:
                QLineEdit.setText(self, text)


RICH_PREFIX = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">'


class TextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptRichText(False)
        self.setTabChangesFocus(True)

        self.setOpenLinks(False)
        self.anchorClicked.connect(self.anchorClickedEvent)

    def anchorClickedEvent(self, link):
        executor = QDesktopServices()
        executor.openUrl(link)

    def sizeHint(self):
        return self.minimumSizeHint()

    def setText(self, text):
        text = htmlToPlainText(text)

        urls = re.findall(r'(https?://[^\s]+|file:///[^\s]+)', text)
        if urls:
            beg = 0
            new_text = ''
            for url in urls:
                i = text.index(url, beg)
                new_text += text[beg:i] + '<a href="%s">%s</a>' % (url, url)
                beg = i + len(url)
            new_text += text[beg:]

            text = new_text.replace('\n', '<br>')

        super().setText(text)

    def text(self):
        return self.toPlainText()


class RichTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptRichText(True)
        self.setTabChangesFocus(True)

        self.setOpenLinks(False)
        self.anchorClicked.connect(self.anchorClickedEvent)

    def anchorClickedEvent(self, link):
        executor = QDesktopServices()
        executor.openUrl(link)

    def sizeHint(self):
        return self.minimumSizeHint()

    def setText(self, text):
        if not text.startswith(RICH_PREFIX):
            urls = re.findall(r'(https?://[^\s]+|file:///[^\s]+)', text)
            if urls:
                beg = 0
                new_text = ''
                for url in urls:
                    i = text.index(url, beg)
                    new_text += text[beg:i] + '<a href="%s">%s</a>' % (url, url)
                    beg = i + len(url)
                new_text += text[beg:]

                text = new_text.replace('\n', '<br>')

        super().setText(text)


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptRichText(False)
        self.setTabChangesFocus(True)

    def sizeHint(self):
        return self.minimumSizeHint()

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        text = htmlToPlainText(text)
        self.setPlainText(text)


class RichTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptRichText(True)
        self.setTabChangesFocus(True)

    def sizeHint(self):
        return self.minimumSizeHint()

    def text(self):
        if self.toPlainText():
            return self.toHtml()
        else:
            return ''

    def setText(self, text):
        if not text.startswith(RICH_PREFIX):
            urls = re.findall(r'(https?://[^\s]+|file:///[^\s]+)', text)
            if urls:
                beg = 0
                new_text = ''
                for url in urls:
                    i = text.index(url, beg)
                    new_text += text[beg:i] + '<a href="%s">%s</a>' % (url, url)
                    beg = i + len(url)
                new_text += text[beg:]

                text = new_text.replace('\n', '<br>')

        super().setText(text)


class CalendarWidget(QCalendarWidget):
    DEFAULT_DATE = QDate(2000, 1, 1)
    
    def __init__(self):
        super().__init__()
        
        self._height_fixed = False

        self._today_button = QPushButton(self.tr("Today"))
        self._today_button.clicked.connect(self.updateToday)
        self._clean_button = QPushButton(self.tr("Clean"))
        self._clean_button.clicked.connect(self.cleanDate)
        buttons = QHBoxLayout()
        buttons.addWidget(self._today_button)
        buttons.addWidget(self._clean_button)
        self.layout().addLayout(buttons)
    
    def updateToday(self):
        today = QDate.currentDate()
        self.clicked.emit(today)

    def cleanDate(self):
        self.clicked.emit(self.DEFAULT_DATE)

    def showEvent(self, e):
        if not self._height_fixed:
            self.setFixedHeight(self.height() + self._clean_button.height())
            self._height_fixed = True

        if self.selectedDate() == self.DEFAULT_DATE:
            self.showToday()


class DateEdit(QDateEdit):
    DEFAULT_DATE = QDate(2000, 1, 1)

    def __init__(self, parent=None):
        super().__init__(parent)
        calendar = CalendarWidget()
        calendar.setGridVisible(True)
        self.setCalendarPopup(True)
        self.setCalendarWidget(calendar)
        self.setMinimumWidth(85)

    def clear(self):
        self.setDate(self.DEFAULT_DATE)
        super().clear()

    def showEvent(self, e):
        super().showEvent(e)
        self.__clearDefaultDate()

    def focusInEvent(self, event):
        if not self.isReadOnly():
            self.setDate(self.date())
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.__clearDefaultDate()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            lineEdit = self.findChild(QLineEdit)
            if lineEdit.selectedText() == lineEdit.text():
                self.setDate(self.DEFAULT_DATE)

        super().keyPressEvent(event)

    def __clearDefaultDate(self):
        if self.date() == self.DEFAULT_DATE:
            lineEdit = self.findChild(QLineEdit)
            lineEdit.setCursorPosition(0)
            lineEdit.setText("")


class DateTimeEdit(QDateTimeEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
