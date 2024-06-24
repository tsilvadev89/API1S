from flask import Flask
from flask import render_template
from flask import request
import sqlite3 as sql

app = Flask(__name__)

#conn = sql.connect('database.db')
#conn.execute('DROP TABLE salas')
#conn.execute('CREATE TABLE salas (nome TEXT, elements TEXT, total INTEGER)')
#conn.close()

#conn = sql.connect('database.db')
#conn.execute('DROP TABLE problemas')
#conn.execute('CREATE TABLE problemas (id INTEGER PRIMARY KEY AUTOINCREMENT, problema TEXT, sugestao TEXT)')
#conn.close()

#conn = sql.connect('database.db')
#conn.execute('DROP TABLE reports')
#conn.execute('CREATE TABLE reports (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, sala TEXT, pc TEXT, desc TEXT, problema TEXT, classificacao TEXT, arquivados TEXT)')
#conn.close()


#conn = sql.connect('database.db')
#conn.execute('DROP TABLE arquivados')
#conn.execute('CREATE TABLE arquivados (id INTEGER PRIMARY KEY AUTOINCREMENT, idoriginal INTEVER, data TEXT, sala TEXT, pc TEXT, desc TEXT, problema TEXT, classificacao TEXT, resolucao TEXT)')
#conn.close()

@app.route('/')
@app.route('/index', methods = ['POST', 'GET'])
def index():
   with sql.connect("database.db") as con:
         con.row_factory = sql.Row

         cur = con.cursor()
         cur.execute("SELECT * FROM salas")
         rows = cur.fetchall()
         
         cur.execute("SELECT * FROM problemas")
         problemas = cur.fetchall()

         return render_template("index.html", rows = rows, problemas = problemas)
         con.close()

@app.route('/reports', methods = ['POST', 'GET'])
def reports():
   with sql.connect("database.db") as con:
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute("SELECT * FROM reports WHERE NOT arquivados = ?",("sim",))
         rows = cur.fetchall()
         return render_template("reports.html", rows = rows)
         con.close()
   
@app.route('/oldreports', methods = ['POST', 'GET'])
def oldreports():
   with sql.connect("database.db") as con:
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute("SELECT * FROM reports WHERE arquivados = ?",("sim",))
         rows = cur.fetchall()
         return render_template("oldreports.html", rows = rows)
         con.close()

@app.route('/send', methods = ['POST', 'GET'])
def send():
   if request.method == 'POST':
      try:
         sala = request.form['sala']
         pc = request.form['computador']
         desc = request.form['descricao']
         problema = request.form['problema']
         classificacao = request.form['classificacao']
         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO reports (data,pc,sala,desc,problema,classificacao,arquivados) VALUES (datetime('now'),?,?,?,?,?,?)",(pc,sala,desc,problema,classificacao,"false"))
            con.commit()
      except:
         con.rollback()
      finally:
         return render_template("index.html")
         con.close()

@app.route('/update', methods = ['POST', 'GET'])
def update():
   option = request.form['options']
   with sql.connect("database.db") as con:
      cur = con.cursor()
      cur.execute("UPDATE reports SET arquivados = ? WHERE id="+option,("sim",))
      con.commit()

      with sql.connect("database.db") as con:
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute("SELECT * FROM reports WHERE NOT arquivados = ?",("sim",))
         rows = cur.fetchall()

         return render_template("reports.html", rows = rows)
         con.close()

@app.route('/edit', methods = ['POST', 'GET'])
def edit():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("SELECT nome FROM salas")
   rows = cur.fetchall()
   return render_template('edit.html', rows = rows)

@app.route('/edited', methods = ['POST', 'GET'])
def edited():
   elmnts = ""
   if request.method == 'POST':
      try:
         selected = request.form["selectedvalue"]

         if (request.form['actiontype'] == "add"):
            nome = request.form['txtnew']
            elements = request.form['elementcontent']
            total = request.form['totalcontent']
            with sql.connect("database.db") as con:
               cur = con.cursor()
               cur.execute('INSERT INTO salas (nome, elements, total) VALUES (?, ?, ?)',(nome, elements, total))
               con.commit()
               msg = "Sala criada com sucesso"

         elif (request.form['actiontype'] == "del"):
            nome = request.form['salalist']
            with sql.connect("database.db") as con:
               cur = con.cursor()
               cur.execute("DELETE FROM salas WHERE nome="+nome)
               con.commit()
               msg = "Sala delatada com sucesso"

         elif (request.form['actiontype'] == "save"):
            nome = request.form['salalist']
            elements = request.form['elementcontent']
            total = request.form['totalcontent']
            with sql.connect("database.db") as con:
               cur = con.cursor()
               cur.execute("UPDATE salas SET elements = ?, total = ? WHERE nome="+nome,(elements, total))
               con.commit()
               msg = "Sala modificada com sucesso"

               nome = request.form['salalist']
               with sql.connect("database.db") as con:
                  con.row_factory = sql.Row
                  cur = con.cursor()
                  cur.execute("SELECT * FROM salas WHERE nome="+nome)
                  elmnts = cur.fetchall()

         elif (request.form['actiontype'] == "load"):
            nome = request.form['salalist']
            with sql.connect("database.db") as con:
               con.row_factory = sql.Row
               cur = con.cursor()
               cur.execute("SELECT * FROM salas WHERE nome="+nome)
               elmnts = cur.fetchall()
               msg = "Sala carregada com sucesso"

      except:
         con.rollback()
         msg = ("ERRO")

      finally:
         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute("SELECT nome FROM salas")
         rows = cur.fetchall()
         return render_template("edit.html", rows = rows, selected = selected, msg = msg, elmnts = elmnts)
         con.close()

@app.route('/graficos', methods=['POST', 'GET'])
def graficos():
   with sql.connect("database.db") as con:
      tbl_data, tbl_occur, tbl_tipo = [], [], []
      # CONSULTA LEITURA QUANTIDADE OCORRÊNCIAS ENVOLVENDO HARDWARE
      cur = con.cursor()
      cur.execute("SELECT * FROM reports WHERE classificacao = 'Hardware' AND NOT arquivados = 'sim'")
      hardwareativo = cur.fetchall()
      hardwareativo = len(hardwareativo)
      # CONSULTA LEITURA QUANTIDADE OCORRÊNCIAS ENVOLVENDO SOFTWARE
      cur.execute("SELECT * FROM reports WHERE classificacao = 'Software' AND NOT arquivados = 'sim'")
      softwareativo = cur.fetchall()
      softwareativo = len(softwareativo)
      # CONSULTA LEITURA QUANTIDADE OCORRÊNCIAS ENVOLVENDO OUTROS
      cur.execute("SELECT * FROM reports WHERE classificacao = 'Outro' AND NOT arquivados = 'sim'")
      outrosativo = cur.fetchall()
      outrosativo = len(outrosativo)

      # CONSULTA LEITURA QUANTIDADE OCORRÊNCIAS ENVOLVENDO HARDWARE
      cur = con.cursor()
      cur.execute("SELECT * FROM reports WHERE classificacao = 'Hardware'")
      hardware = cur.fetchall()
      hardware = len(hardware)
      # CONSULTA LEITURA QUANTIDADE OCORRÊNCIAS ENVOLVENDO SOFTWARE
      cur.execute("SELECT * FROM reports WHERE classificacao = 'Software'")
      software = cur.fetchall()
      software = len(software)
      # CONSULTA LEITURA QUANTIDADE OCORRÊNCIAS ENVOLVENDO OUTROS
      cur.execute("SELECT * FROM reports WHERE classificacao = 'Outro'")
      outro = cur.fetchall()
      outro = len(outro)

      # CONSULTA LEITURA ORDENDADA PARA ALIMENTAÇÃO TABELA ULTIMOS REGISTROS
      cur.execute(
         "SELECT * FROM reports WHERE arquivados = 'false' ORDER BY ID DESC")
      #rows = cur.fetchall()
      tbl_list = cur.fetchall()

      # CONSULTA LEITURA DE CADA MES HARDWARE
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-01-%' AND classificacao = 'Hardware'")
      mes1 = cur.fetchall()
      mes1 = len(mes1)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-02-%' AND classificacao = 'Hardware'")
      mes2 = cur.fetchall()
      mes2 = len(mes2)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-03-%' AND classificacao = 'Hardware'")
      mes3 = cur.fetchall()
      mes3 = len(mes3)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-04-%' AND classificacao = 'Hardware'")
      mes4 = cur.fetchall()
      mes4 = len(mes4)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-05-%' AND classificacao = 'Hardware'")
      mes5 = cur.fetchall()
      mes5 = len(mes5)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-06-%' AND classificacao = 'Hardware'")
      mes6 = cur.fetchall()
      mes6 = len(mes6)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-07-%' AND classificacao = 'Hardware'")
      mes7 = cur.fetchall()
      mes7 = len(mes7)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-08-%' AND classificacao = 'Hardware'")
      mes8 = cur.fetchall()
      mes8 = len(mes8)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-09-%' AND classificacao = 'Hardware'")
      mes9 = cur.fetchall()
      mes9 = len(mes9)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-10-%' AND classificacao = 'Hardware'")
      mes10 = cur.fetchall()
      mes10 = len(mes10)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-11-%' AND classificacao = 'Hardware'")
      mes11 = cur.fetchall()
      mes11 = len(mes11)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-12-%' AND classificacao = 'Hardware'")
      mes12 = cur.fetchall()
      mes12 = len(mes12)
      listahardware = [mes1, mes2, mes3, mes4, mes5, mes6, mes7, mes8, mes9, mes10, mes11, mes12]
      # CONSULTA LEITURA DE CADA MES SOFTWARE
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-01-%' AND classificacao = 'Software'")
      mes1 = cur.fetchall()
      mes1 = len(mes1)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-02-%' AND classificacao = 'Software'")
      mes2 = cur.fetchall()
      mes2 = len(mes2)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-03-%' AND classificacao = 'Software'")
      mes3 = cur.fetchall()
      mes3 = len(mes3)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-04-%' AND classificacao = 'Software'")
      mes4 = cur.fetchall()
      mes4 = len(mes4)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-05-%' AND classificacao = 'Software'")
      mes5 = cur.fetchall()
      mes5 = len(mes5)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-06-%' AND classificacao = 'Software'")
      mes6 = cur.fetchall()
      mes6 = len(mes6)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-07-%' AND classificacao = 'Software'")
      mes7 = cur.fetchall()
      mes7 = len(mes7)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-08-%' AND classificacao = 'Software'")
      mes8 = cur.fetchall()
      mes8 = len(mes8)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-09-%' AND classificacao = 'Software'")
      mes9 = cur.fetchall()
      mes9 = len(mes9)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-10-%' AND classificacao = 'Software'")
      mes10 = cur.fetchall()
      mes10 = len(mes10)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-11-%' AND classificacao = 'Software'")
      mes11 = cur.fetchall()
      mes11 = len(mes11)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-12-%' AND classificacao = 'Software'")
      mes12 = cur.fetchall()
      mes12 = len(mes12)
      listasoftware = [mes1, mes2, mes3, mes4, mes5, mes6, mes7, mes8, mes9, mes10, mes11, mes12]
      # CONSULTA LEITURA DE CADA MES OUTROS
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-01-%' AND classificacao = 'Outro'")
      mes1 = cur.fetchall()
      mes1 = len(mes1)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-02-%' AND classificacao = 'Outro'")
      mes2 = cur.fetchall()
      mes2 = len(mes2)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-03-%' AND classificacao = 'Outro'")
      mes3 = cur.fetchall()
      mes3 = len(mes3)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-04-%' AND classificacao = 'Outro'")
      mes4 = cur.fetchall()
      mes4 = len(mes4)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-05-%' AND classificacao = 'Outro'")
      mes5 = cur.fetchall()
      mes5 = len(mes5)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-06-%' AND classificacao = 'Outro'")
      mes6 = cur.fetchall()
      mes6 = len(mes6)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-07-%' AND classificacao = 'Outro'")
      mes7 = cur.fetchall()
      mes7 = len(mes7)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-08-%' AND classificacao = 'Outro'")
      mes8 = cur.fetchall()
      mes8 = len(mes8)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-09-%' AND classificacao = 'Outro'")
      mes9 = cur.fetchall()
      mes9 = len(mes9)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-10-%' AND classificacao = 'Outro'")
      mes10 = cur.fetchall()
      mes10 = len(mes10)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-11-%' AND classificacao = 'Outro'")
      mes11 = cur.fetchall()
      mes11 = len(mes11)
      cur.execute("SELECT * FROM reports WHERE data LIKE '%-12-%' AND classificacao = 'Outro'")
      mes12 = cur.fetchall()
      mes12 = len(mes12)
      listaoutros = [mes1, mes2, mes3, mes4, mes5, mes6, mes7, mes8, mes9, mes10, mes11, mes12]

      # TRATAMENTO PARA LISTAR FORMA INVERSA OS ITENS PARA ALIMENTAÇÃO DAS TABELAS
      for i in range(len(tbl_list)):
         t = (tbl_list[i])
         tbl_data.insert(i, t[2])
         tbl_occur.insert(i, t[4])
         tbl_tipo.insert(i, t[6])

      # CONSULTA LEITURA QUANTIDADE OCORRÊNCIAS ENVOLVENDO OUTROS
      cur.execute("SELECT * FROM reports")
      rows = cur.fetchall()
      return render_template("graficos.html", hardwareativo=hardwareativo, softwareativo=softwareativo, outrosativo=outrosativo, hardware=hardware, software=software, outro=outro, tbl_data=tbl_data, tbl_occur=tbl_occur, tbl_tipo=tbl_tipo, rows=rows, listahardware = listahardware, listasoftware = listasoftware, listaoutros = listaoutros)
      con.close()

if __name__ == '__main__':
    app.run(debug=True)
