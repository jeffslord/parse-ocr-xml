import tabula
import os

fname = "pdfs/pdf6"
pdfname = fname + ".pdf"
csvname = fname + ".csv"
pandas_options = {'header': None}
df = tabula.read_pdf(pdfname, multiple_tables=False,
                     guess=True, pandas_options=pandas_options)

toDelete = []
# for index, row in df.iterrows():
#     print(row)
print(df)

try:
    os.remove(csvname)
except OSError:
    pass
tabula.convert_into(pdfname, csvname, output_format="csv")
