from PyQt4.QtCore import QObject
from PyQt4.QtSql import QSqlDatabase, QSqlQuery

class FieldTypes():
    String = 1
    ShortString = 2
    Number = 3
    Text = 4
    Money = 5
    Date = 6
    BigInt = 7
    Image = 8
    Value = 9
    Status = 10
    DateTime = 11
    EdgeImage = 12
    
    Mask = int('FF', 16)  # 0xFF
    Checkable = int('100', 16)  # 0x100
    Disabled = int('200', 16)  # 0x200

class CollectionField():
    def __init__(self, id, name, title, type):
        self.id = id
        self.name = name
        self.title = title
        self.type = type

class CollectionFieldsBase(QObject):
    def __init__(self, parent=None):
        from Collection.CollectionFields import FieldTypes as Type
        super(CollectionFieldsBase, self).__init__(parent)
        
        fields = [
                ('id', self.tr("ID"), Type.BigInt),

                ('title', self.tr("Name"), Type.String),
                ('value', self.tr("Value"), Type.Money),
                ('unit', self.tr("Unit"), Type.String),
                ('country', self.tr("Country"), Type.String),
                ('year', self.tr("Year"), Type.Number),
                ('period', self.tr("Period"), Type.String),
                ('mint', self.tr("Mint"), Type.String),
                ('mintmark', self.tr("Mint mark"), Type.ShortString),
                ('issuedate', self.tr("Date of issue"), Type.Date),
                ('type', self.tr("Type"), Type.String),
                ('series', self.tr("Series"), Type.String),
                ('subjectshort', self.tr("Subject"), Type.String),
                ('status', self.tr("Status"), Type.Status),
                ('metal', self.tr("Metal"), Type.String),
                ('fineness', self.tr("Fineness"), Type.Number),
                ('form', self.tr("Form"), Type.String),
                ('diameter', self.tr("Diameter"), Type.Value),
                ('thick', self.tr("Thick"), Type.Value),
                ('mass', self.tr("Mass"), Type.Value),
                ('grade', self.tr("Grade"), Type.String),
                ('edge', self.tr("Type"), Type.String),
                ('edgelabel', self.tr("Label"), Type.String),
                ('obvrev', self.tr("ObvRev"), Type.String),
                ('quality', self.tr("Quality"), Type.String),
                ('mintage', self.tr("Mintage"), Type.BigInt),
                ('dateemis', self.tr("Emission period"), Type.String),
                ('catalognum1', self.tr("1#"), Type.String),
                ('catalognum2', self.tr("2#"), Type.String),
                ('catalognum3', self.tr("3#"), Type.String),
                ('catalognum4', self.tr("#4"), Type.String),
                ('rarity', self.tr("Rarity"), Type.String),
                ('price1', self.tr("Fine"), Type.Money),
                ('price2', self.tr("VF"), Type.Money),
                ('price3', self.tr("XF"), Type.Money),
                ('price4', self.tr("Unc"), Type.Money),
                ('variety', self.tr("Variety"), Type.String),
                ('obversevar', self.tr("Obverse"), Type.String),
                ('reversevar', self.tr("Reverse"), Type.String),
                ('edgevar', self.tr("Edge"), Type.String),
                ('paydate', self.tr("Date"), Type.Date),
                ('payprice', self.tr("Price"), Type.Money),
                ('totalpayprice', self.tr("Paid"), Type.Money),
                ('saller', self.tr("Saller"), Type.String),
                ('payplace', self.tr("Place"), Type.String),
                ('payinfo', self.tr("Info"), Type.Text),
                ('saledate', self.tr("Date"), Type.Date),
                ('saleprice', self.tr("Price"), Type.Money),
                ('totalsaleprice', self.tr("Bailed"), Type.Money),
                ('buyer', self.tr("Buyer"), Type.String),
                ('saleplace', self.tr("Place"), Type.String),
                ('saleinfo', self.tr("Info"), Type.Text),
                ('note', self.tr("Note"), Type.Text),
                ('image', self.tr("Image"), Type.Image),
                ('obverseimg', self.tr("Obverse"), Type.Image),
                ('obversedesign', self.tr("Design"), Type.Text),
                ('obversedesigner', self.tr("Designer"), Type.String),
                ('reverseimg', self.tr("Reverse"), Type.Image),
                ('reversedesign', self.tr("Design"), Type.Text),
                ('reversedesigner', self.tr("Designer"), Type.String),
                ('edgeimg', self.tr("Edge"), Type.EdgeImage),
                ('subject', self.tr("Subject"), Type.Text),
                ('photo1', self.tr("Photo 1"), Type.Image),
                ('photo2', self.tr("Photo 2"), Type.Image),
                ('photo3', self.tr("Photo 3"), Type.Image),
                ('photo4', self.tr("Photo 4"), Type.Image),
                ('defect', self.tr("Defect"), Type.String),
                ('storage', self.tr("Storage"), Type.String),
                ('features', self.tr("Features"), Type.Text),
                ('createdat', self.tr("Created at"), Type.DateTime),
                ('updatedat', self.tr("Updated at"), Type.DateTime)
            ]

        self.fields = []
        for id, field in enumerate(fields):
            self.fields.append(CollectionField(id, field[0], field[1], field[2]))
            setattr(self, self.fields[id].name, self.fields[id])
        
        self.userFields = list(self.fields)
        for item in [self.id, self.createdat, self.updatedat]:
            self.userFields.remove(item)
    
    def field(self, id):
        return self.fields[id]

    def __iter__(self):
        self.index = 0
        return self
    
    def __next__(self):
        if self.index == len(self.fields):
            raise StopIteration
        self.index = self.index + 1
        return self.fields[self.index-1]

class CollectionFields(CollectionFieldsBase):
    def __init__(self, db=QSqlDatabase(), parent=None):
        super(CollectionFields, self).__init__(parent)
        self.db = db
        
        if 'fields' not in self.db.tables():
            self.create(self.db)
        
        query = QSqlQuery(self.db)
        query.prepare("SELECT * FROM fields")
        query.exec_()
        self.userFields = []
        self.disabledFields = []
        while query.next():
            record = query.record()
            fieldId = record.value('id')
            field = self.field(fieldId)
            field.title = record.value('title')
            field.enabled = bool(record.value('enabled'))
            if field.enabled:
                self.userFields.append(field)
            else:
                self.disabledFields.append(field)
    
    def save(self):
        self.db.transaction()

        for field in self.fields:
            query = QSqlQuery(self.db)
            query.prepare("UPDATE fields SET title=?, enabled=? WHERE id=?")
            query.addBindValue(field.title)
            query.addBindValue(int(field.enabled))
            query.addBindValue(field.id)
            query.exec_()

        self.db.commit()
    
    @staticmethod
    def create(db=QSqlDatabase()):
        db.transaction()
        
        sql = """CREATE TABLE fields (
            id INTEGER NOT NULL PRIMARY KEY,
            title CHAR,
            enabled INTEGER)"""
        QSqlQuery(sql, db)
        
        fields = CollectionFieldsBase()
        
        for field in fields:
            query = QSqlQuery(db)
            query.prepare("""INSERT INTO fields (id, title, enabled)
                VALUES (?, ?, ?)""")
            query.addBindValue(field.id)
            query.addBindValue(field.title)
            enabled = field in fields.userFields
            query.addBindValue(int(enabled))
            query.exec_()
        
        db.commit()
