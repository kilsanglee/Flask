import os
import  datetime
from datetime import datetime
from flask import render_template
from flask import request, redirect, url_for
from . import pds_bp
import cx_Oracle

file_dir = 'static/pds/files/'

# 오라클 DB 연동하기
def  get_db_connection():
    dsn = cx_Oracle.makedsn('localhost','1521', service_name='XE')
    connection = cx_Oracle.connect(user='majustory',password='1234', dsn=dsn)
    return connection

@pds_bp.route('/pds_delete')
def  pds_delete():

    # GET 방법으로 값 받아오기
    idx = request.args.get("idx")
    files = request.args.get("files")

    del_file = file_dir + files

    # 파일이 존재 하면 삭제.
    if os.path.exists(del_file):
        os.remove(del_file)

    print("===> pds_delete ", idx, files)
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
                   delete from pds where idx = :1
                   """
                   , (idx,))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('pds_bp.pds_list'))


@pds_bp.route('/pds_update', methods=['post'])
def board_update():
  connection = get_db_connection()
  cursor = connection.cursor()

  idx = request.form['idx']
  sname = request.form['sname']
  title = request.form['title']
  content = request.form['content']
  file = request.files['file']

  if file.filename != "" :
      cursor.execute("""
                     select * from pds where idx = :1
                     """
                     , (idx,))
      row = cursor.fetchone()
      result = ""
      if row:
          column_names = [desc[0].lower() for desc in cursor.description]
          result = dict(zip(column_names, row))

      del_file = file_dir + result['files']
      if os.path.exists(del_file):
          print("===>수정 del_file : ", del_file)
          os.remove(del_file)

      file_path = os.path.join(file_dir, file.filename)
      filename = ""
      if os.path.exists(file_path):
          name, ext = os.path.splitext(file.filename)
          timestr = datetime.now().strftime("%H%M%S")
          filename = f"{name}_{timestr}{ext}"
          file_path = os.path.join(file_dir, filename)
          file.save(file_path)

      else:
          filename = file.filename
          file.save(file_path)

      cursor.execute(
          '''
             update pds 
             set sname =:1, title =:2, content=:3 , files = :4
             where idx=:5          
          ''', (sname, title, content, filename ,idx)
      )
      connection.commit()
  else:
      cursor.execute(
          '''
             update pds 
             set sname =:1, title =:2, content=:3 
             where idx=:4          
          ''', (sname, title, content, idx)
      )
      connection.commit()


  cursor.close()
  connection.close()
  return redirect(url_for('pds_bp.pds_list'))

@pds_bp.route('/pds_save', methods=['post'])
def pds_save():
      from datetime import datetime
      file = request.files['file']

      file_path = os.path.join(file_dir, file.filename)
      filename = ""
     # 파일을 먼저 처리 해야 합니다.
      if os.path.exists(file_path):
          name, ext = os.path.splitext(file.filename)
          timestr = datetime.now().strftime("%H%M%S")
          filename = f"{name}_{timestr}{ext}"
          print("==> filename:",filename)
          file_path = os.path.join(file_dir, filename)
          file.save(file_path)
      else:
          file_name = file.filename
          file.save(file_path)

      sname = request.form['sname']
      title = request.form['title']
      content = request.form['content']
      connection = get_db_connection()
      cursor = connection.cursor()
      cursor.execute(
          '''
             insert into pds(idx, sname, title, content,files,cnt)
             values(idx_pds.nextval, :1, :2,:3,:4, 0)
          ''',(sname, title,content,filename)
      )
      
      connection.commit()
      cursor.close()
      connection.close()

      return redirect(url_for('pds_bp.pds_list'))


@pds_bp.route('/pds_form')
def pds_form():
    return render_template('pds/form.html')


@pds_bp.route('/pds_list')
def pds_list():

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("select idx, sname, title, content, files, cnt  "
                   " from  pds  "
                   " order  by  idx  desc")

    column_names = [desc[0].lower() for desc in cursor.description]

    '''
    column_names = []
    for desc in cursor.description:
        column_names.append(desc[0].lower())
    '''

    rows = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    '''
    rows = []
    for row in cursor.fetchall():
        rows.append(dict(zip(column_names, row)))
    '''
    cursor.close()
    connection.close()
    return render_template('pds/list.html', rows=rows)

@pds_bp.route("/pds_edit")
def  board_edit():
    # GET 방법으로 값 받아오기
    idx = request.args.get("idx")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        '''
           update pds 
           set cnt = cnt + 1
           where idx=:1          
        ''', (idx,)
    )
    connection.commit()

    cursor.execute("""
                   select * from pds where idx = :1
                   """
                   , (idx,))
    row = cursor.fetchone()

    # 튜플값을 딕셔너리로 변경해서 컬럼이름을 사용할 수 있도록 도와준다.
    if row :
        column_names = [desc[0].lower() for desc in cursor.description]
        result = dict(zip(column_names, row))

        return  render_template('pds/edit.html' , row= result )

    cursor.close()
    connection.close()

@pds_bp.route('/pds_insert')
def pds_insert():

      from faker import Faker
      fake = Faker('ko-KR')
      """
      fake.address(): 한국 주소 형식을 생성합니다.
      fake.company(): 한국 회사명을 생성합니다.
      fake.job(): 한국 직업명을 생성합니다.
      """
      connection = get_db_connection()
      cursor = connection.cursor()

      for i in range(100):
          sname = fake.name()
          title = fake.company()
          content = fake.text()

          cursor.execute(
              '''
                 insert into board(idx, sname, title, content,cnt)
                 values(idx_board.nextval, :1, :2,:3, 0)
              ''',(sname, title,content)
          )
          connection.commit()

      cursor.close()
      connection.close()

      return redirect(url_for('pds_bp.board_list'))