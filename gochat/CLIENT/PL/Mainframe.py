#MAIN FRAME
from time import *
import tkinter as tk
from tkinter import messagebox
from Login import *
import sys
sys.path.append('..')
from BLL.LoginServices import loginServices
from BLL.UMSservices import UMSservices
from DL.User import *


import socket
from threading import Thread

class Mainframe:
	def __init__(self,uid,usn):
		self.userid=uid
		self.username=usn
		self.root=tk.Tk()
		self.root.title('Mainframe')
		self.root.geometry('')
		
		self.menubar=tk.Menu(self.root)
		self.Logoutmenu= tk.Menu(self.menubar, tearoff=0)
		self.Logoutmenu.add_command(label="Logout",command=self.Logout)
		self.Logoutmenu.add_command(label="Change Password",command=self.Changepasswd)
		self.Logoutmenu.add_command(label="Exit", command=self.root.quit)
		self.menubar.add_cascade(label="LogOut", menu=self.Logoutmenu)
		
		self.ums= tk.Menu(self.menubar, tearoff=0)
		self.ums.add_command(label="Manage User",command=self.Manageuser)
		self.ums.add_command(label="Manage Profile",command=self.Manageprofile)
		self.menubar.add_cascade(label="UMS", menu=self.ums)
		
		self.chat= tk.Menu(self.menubar, tearoff=0)
		self.chat.add_command(label="Chat", command=self.start_chat)
		self.menubar.add_cascade(label="CHAT", menu=self.chat)
		
		self.root.config(menu=self.menubar)
		self.root.mainloop()
	def Logout(self):
		loginServices.logout()
		
	def Changepasswd(self):
		self.root.destroy()
		c=Changepasswd(self.userid,self.username)
	
	def Manageuser(self):
		self.root.destroy()
		m=Manageuser(self.userid,self.userid)
		
	def Manageprofile(self):
		self.root.destroy()
		m=Manageprofile(self.userid,self.username)
		
	def start_chat(self):
		self.client=socket.socket()
		portno=UMSservices.GetPortno()
		self.client.connect(('127.0.0.1',portno))
		self.client.send(self.username.encode())
		c=Chat(self.username,self.client)
		
		
class Chat:
	def __init__(self,usr,client):
		self.username=str(usr)
		UMSservices.Active(self.username)
		self.client=client
		self.root=tk.Tk()
		self.root.geometry()
		self.Frame1 = tk.LabelFrame(self.root,text='Users',bg='cyan',width=200,height=380,bd=1)
		self.Frame1.pack(padx=1,pady=1,side='left') 

		self.Frame2 = tk.LabelFrame(self.root,text='Chatbox',width=200,height=320,bd=1)
		self.Frame2.pack(padx=1,pady=1,side='left')
		
		
		self.chatbox=tk.Text(self.Frame2,height=20,width=50)
		self.chatbox.grid(row=0,column=0,padx=5,pady=5)
		self.scroll=tk.Scrollbar(self.Frame2,orient='vertical',command=self.chatbox.yview)
		self.scroll.grid(row=0,column=1,sticky='e')
		self.chatbox['yscrollcommand']=self.scroll.set
		self.message=tk.Text(self.Frame2,width=40,height=1)
		self.message.grid(sticky='w',row=1,column=0,padx=5)
		self.send=tk.Button(self.Frame2,text='Send',width=9,command=self.btn_send_clicked)
		self.send.grid(sticky='e',row=1,column=0)
		self.chatbox.config(state='disable')
		
		self.userbox=tk.Text(self.Frame1,height=15,width=30)
		self.userbox.grid(row=0,column=0,padx=5,pady=5)
		
		tk.Label(self.Frame1,text='START_CHAT_WITH').grid(row=1,column=0,padx=20,pady=10)
		self.Chat_with=tk.Entry(self.Frame1)
		self.Chat_with.grid(row=2,column=0,padx=20,pady=7)
		self.send.config(state='disable')
		self.contact=tk.Button(self.Frame1,text='Start_Chat',width=9,command=self.Contact)
		self.contact.grid(row=3,column=0,padx=20,pady=7)
		self.exit=tk.Button(self.Frame1,text='Stop_Chat',width=9,command=self.Stop_Chat)
		self.exit.grid(row=4,column=0,padx=20,pady=7)
		self.onl_list=Thread(target=self.online_list)
		self.onl_list.start()
		self.root.mainloop()
		
	def Contact(self):
		self.send.config(state='normal')
		self.to_user=self.Chat_with.get()
		self.client.send(self.to_user.encode())
		self.Start(self.to_user)
		self.Chat_with.delete(0,'end')
		self.Chat_with.config(state='disable')
		self.contact.config(state='disable')
		self.fname=str(self.username)+'_'+str(self.to_user)+'.txt'
		f=open(self.fname,'r+')
		m=f.read()
		self.chatbox.config(state='normal')
		self.chatbox.insert('end',m)
		self.chatbox.config(state='disable')
		f.close()
		
	def Stop_Chat(self):
		UMSservices.InActive(str(self.username))
		self.root.destroy()
		
		
	def btn_send_clicked(self):
		self.chatbox.config(state='normal')
		self.msg=self.message.get(1.0,'end')
		self.chatbox.insert('end',self.username+' : '+self.msg+'\n')
		self.chatbox.config(state='disable')
		self.chatbox.yview('end')
		self.client.send(self.msg.encode())
		self.message.delete(1.0,'end')
		f=open(self.fname,'a')
		f.write(str(self.username)+' : '+self.msg)
		f.close()
		

	def online_list(self):
		while True:
			self.userbox.config(state='normal')
			self.online=UMSservices.online_user()
			self.userbox.delete(1.0,'end')
			a=(self.username,)
			self.online.remove(a)
			for i in self.online:
				self.userbox.insert('end',i)
				self.userbox.insert('end',str('\n'))
			self.userbox.config(state='disable')
			sleep(10)

	def Start(self,from_user):
		r=Thread(target=self.Recieve,args=(from_user,))
		r.start()
	
	def Recieve(self,user):
		while True:
			self.mssg=self.client.recv(1024).decode()
			self.chatbox.config(state='normal')
			self.chatbox.insert('end',user+' : '+self.mssg+'\n')
			self.chatbox.config(state='disable')
			f=open(self.fname,'a')
			f.write(str(user)+' : '+self.mssg)
			f.close()

class Changepasswd:		
	def __init__(self,uid,un):
		self.user_id=uid
		self.username=un
		self.rt=tk.Tk()
		self.rt.title('Changepassword')
		self.rt.geometry('')
		
		tk.Label(self.rt,text='Welcome ').grid(row=0,column=0,padx=20,pady=10)
		tk.Label(self.rt,text='Old Password').grid(row=2,column=0,padx=20,pady=10)
		tk.Label(self.rt,text='New Password').grid(row=3,column=0,padx=20,pady=10)
		tk.Label(self.rt,text='Confirm Password').grid(row=4,column=0,padx=20,pady=10)
		
		self.old=tk.Entry(self.rt)
		self.old.grid(row=2,column=1,padx=20,pady=10)
		self.new=tk.Entry(self.rt)
		self.new.grid(row=3,column=1,padx=20,pady=10)
		self.cnf=tk.Entry(self.rt)
		self.cnf.grid(row=4,column=1,padx=20,pady=10)
		
		self.submit=tk.Button(self.rt,text='Submit',command=self.submit)
		self.submit.grid(row=5,column=0,padx=20,pady=10)
		self.cancel=tk.Button(self.rt,text='Cancel',command=self.cancel)
		self.cancel.grid(row=5,column=1,padx=20,pady=10)
		self.rt.mainloop()
	def submit(self):
		if self.new.get()==self.cnf.get():
			if(loginServices.changePassword(str(self.username),self.old.get(),self.cnf.get())):
				messagebox.showinfo('Success','Password Changed')
				self.rt.destroy()
				m=Mainframe(self.user_id,self.self.username)
			else:
				messagebox.showinfo('Error','Password Mismatched')
		else:
			messagebox.showinfo('Error','New and Confirm Password\nMismatched')
	def cancel(self):
		self.rt.destroy()
		m=Mainframe(self.user_id,self.username)
	
	
		
class Manageuser:		
	def __init__(self,uid,un):
		self.usid=uid
		self.username=un
		self.root=tk.Tk()
		self.root.title('ManageUser')
		self.root.geometry('')
		tk.Label(self.root,text='UserId').grid(row=0,column=0,padx=20,pady=10)
		tk.Label(self.root,text='UserName').grid(row=1,column=0,padx=20,pady=10)
		tk.Label(self.root,text='UserType').grid(row=2,column=0,padx=20,pady=10)
		tk.Label(self.root,text='UserStatus').grid(row=3,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Name').grid(row=4,column=0,padx=20,pady=10)
		tk.Label(self.root,text='E-mail').grid(row=5,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Contact').grid(row=6,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Address').grid(row=7,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Gender').grid(row=8,column=0,padx=20,pady=10)
		
		self.userid=tk.Entry(self.root)
		self.userid.grid(row=0,column=1,padx=20,pady=10)
		self.username=tk.Entry(self.root)
		self.username.grid(row=1,column=1,padx=20,pady=10)
		self.name=tk.Entry(self.root)
		self.name.grid(row=4,column=1,padx=20,pady=10)
		self.email=tk.Entry(self.root)
		self.email.grid(row=5,column=1,padx=20,pady=10)
		self.contact=tk.Entry(self.root)
		self.contact.grid(row=6,column=1,padx=20,pady=10)
		self.address=tk.Text(self.root,height=4,width=15)
		self.address.grid(row=7,column=1,padx=20,pady=10)
		
		self.v=tk.StringVar()
		self.v.set('Active')
		self.r1=tk.Radiobutton(text='Active',variable=self.v,value='Active')
		self.r1.grid(row=3,column=1,padx=20,pady=10)
		self.r2=tk.Radiobutton(text='InActive',variable=self.v,value='InActive')
		self.r2.grid(row=3,column=2,padx=20,pady=10)
		
		self.g=tk.StringVar()
		self.g.set('Male')
		self.r3=tk.Radiobutton(text='Male',variable=self.g,value='Male')
		self.r3.grid(row=8,column=1,padx=20,pady=10)
		self.r4=tk.Radiobutton(text='Female',variable=self.g,value='Female')
		self.r4.grid(row=8,column=2,padx=20,pady=10)
		
		self.type=tk.StringVar()
		self.type.set('admin')
		self.usertype=tk.OptionMenu(self.root,self.type,'admin','user')
		self.usertype.grid(row=2,column=1,padx=20,pady=10)
		
		
		self.first=tk.Button(self.root,text='First',width=9,command=self.btn_first_clicked)
		self.first.grid(row=9,column=0,padx=20,pady=10)
		self.previous=tk.Button(self.root,text='Previous',width=9,command=self.btn_previous_clicked)
		self.previous.grid(row=9,column=1,padx=20,pady=10)
		self.next=tk.Button(self.root,text='Next',width=9,command=self.btn_next_clicked)
		self.next.grid(row=9,column=2,padx=20,pady=10)
		self.last=tk.Button(self.root,text='Last',width=9,command=self.btn_last_clicked)
		self.last.grid(row=9,column=3,padx=20,pady=10)
		
		self.add=tk.Button(self.root,text='Add',width=9,command=self.btn_add_clicked)
		self.add.grid(row=10,column=0,padx=20,pady=10)
		self.edit=tk.Button(self.root,text='Edit',width=9,command=self.btn_edit_clicked)
		self.edit.grid(row=10,column=1,padx=20,pady=10)
		self.save=tk.Button(self.root,text='Save',width=9,command=self.btn_save_clicked)
		self.save.grid(row=10,column=2,padx=20,pady=10)
		self.cancel=tk.Button(self.root,text='Cancel',width=9,command=self.cancel)
		self.cancel.grid(row=10,column=3,padx=20,pady=10)
		
		self.userlist=UMSservices.view()
		self.current_index=0
		self.addeditflag='view'
		self.save.config(state='disabled')
		self.showRecord()
		self.root.mainloop()
		
	def cancel(self):
		if self.addeditflag=='view':
			self.root.destroy()
			m=Mainframe(self.usid,self.username)
		else:
			self.addeditflag='view'
			self.showRecord()
	
	def showRecord(self):
		self.enableAll()
		user=self.userlist[self.current_index]
		self.userid.delete(0,'end')
		self.userid.insert(0,str(user.getUserid()))
		self.username.delete(0,'end')
		self.username.insert(0,str(user.getUsername()))
		self.name.delete(0,'end')
		self.name.insert(0,str(user.getName()))
		self.email.delete(0,'end')
		self.email.insert(0,str(user.getEmail()))
		self.contact.delete(0,'end')
		self.contact.insert(0,str(user.getContact()))
		self.address.delete(1.0,'end')
		self.address.insert(1.0,str(user.getAddress()))
		self.type.set(str(user.getUsertype()))
		if user.getUserstatus():
			self.v.set('Active')
		else:
			self.v.set('InActive')
		if user.getGender():
			self.g.set('Male')
		else:
			self.g.set('Female')
		self.disableAll()
		
		self.first.config(state='normal')
		self.next.config(state='normal')
		self.previous.config(state='normal')
		self.last.config(state='normal')
		if self.current_index==0:
			self.first.config(state='disable')
			self.previous.config(state='disable')
		if self.current_index==len(self.userlist)-1:
			self.last.config(state='disable')
			self.next.config(state='disable')
			
				
	def enableAll(self):
		self.userid.config(state='normal')
		self.username.config(state='normal')
		self.usertype.config(state='normal')
		self.r1.config(state='normal')
		self.r2.config(state='normal')
		self.r3.config(state='normal')
		self.r4.config(state='normal')
		self.name.config(state='normal')
		self.email.config(state='normal')
		self.contact.config(state='normal')
		self.address.config(state='normal')
		
		
	def disableAll(self):
		self.userid.config(state='disable')
		self.username.config(state='disable')
		self.usertype.config(state='disable')
		self.r1.config(state='disable')
		self.r2.config(state='disable')
		self.r3.config(state='disable')
		self.r4.config(state='disable')
		self.name.config(state='disable')
		self.email.config(state='disable')
		self.contact.config(state='disable')
		self.address.config(state='disable')
		
	def btn_first_clicked(self):
		self.current_index=0
		self.showRecord()
		
	def btn_last_clicked(self):
		self.current_index=len(self.userlist)-1
		self.showRecord()
		
	def btn_next_clicked(self):
		self.current_index+=1
		self.showRecord()
		
	def btn_previous_clicked(self):
		self.current_index-=1
		self.showRecord()
		
	def btn_edit_clicked(self):
		self.addeditflag='edit'
		self.enableAll()
		self.save.config(state='normal')
		self.userid.config(state='disable')
		self.username.config(state='disable')
		self.first.config(state='disable')
		self.next.config(state='disable')
		self.previous.config(state='disable')
		self.last.config(state='disable')
		self.edit.config(state='disable')
		self.add.config(state='disable')
	
	def btn_add_clicked(self):
		self.addeditflag='add'
		self.enableAll()
		self.save.config(state='normal')
		
		self.userid.delete(0,'end')
		self.userid.config(state='disable')
		self.username.delete(0,'end')
	
		
		self.name.delete(0,'end')
		self.email.delete(0,'end')
		self.contact.delete(0,'end')
		self.address.delete(1.0,'end')
		
		self.v.set('Active')
		self.g.set('Male')
		self.type.set('admin')
		
		self.first.config(state='disable')
		self.next.config(state='disable')
		self.previous.config(state='disable')
		self.last.config(state='disable')
		self.edit.config(state='disable')
		self.add.config(state='disable')
		
	def btn_save_clicked(self):
		usr=user()
		if self.type.get()=='admin':
			usr.setUsertype('admin')
		else:
			usr.setUsertype('user')
			
		if self.v.get()=='Active':
			usr.setUserstatus(1)
		else:
			usr.setUserstatus(0)
		
		usr.setName(self.name.get())
		usr.setEmail(self.email.get())
		usr.setContact(self.contact.get())
		usr.setAddress(self.address.get(1.0,'end'))
		
		if self.g.get()=='Male':
			usr.setGender(1)
		else:
			usr.setGender(0)
			
		if self.addeditflag=='add':
			self.usn=self.username.get()
			usr.setUsername(self.usn)
			self.paswd='123456'
			usr.setPassword(self.paswd)
			if UMSservices.add(usr):
				messagebox.showinfo('Success','Record added\nPassword:'+str(self.paswd))
				
		elif self.addeditflag=='edit':
			usr.setUserid(int(self.userid.get()))
			if UMSservices.update(usr):
				messagebox.showinfo('Success','Record updated')
		
		self.save.config(state='disable')
		self.add.config(state='normal')
		self.edit.config(state='normal')
		
		self.userlist=UMSservices.view()
		if self.addeditflag=='add':
			self.current_index=len(self.userlist)-1
			self.root.destroy()
			l=Login()
		self.addeditflag=='view'
		self.showRecord()
			
class Manageprofile:		
	def __init__(self,uid,un):
		self.uid=uid
		self.un=un
		self.root=tk.Tk()
		self.root.title('ManageProfile')
		self.root.geometry('')
		tk.Label(self.root,text='UserId').grid(row=0,column=0,padx=20,pady=10)
		tk.Label(self.root,text='UserName').grid(row=1,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Name').grid(row=2,column=0,padx=20,pady=10)
		tk.Label(self.root,text='E-mail').grid(row=3,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Contact').grid(row=4,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Address').grid(row=5,column=0,padx=20,pady=10)
		tk.Label(self.root,text='Gender').grid(row=6,column=0,padx=20,pady=10)
		
		self.userid=tk.Entry(self.root)
		self.userid.grid(row=0,column=1,padx=20,pady=10)
		self.username=tk.Entry(self.root)
		self.username.grid(row=1,column=1,padx=20,pady=10)
		self.name=tk.Entry(self.root)
		self.name.grid(row=2,column=1,padx=20,pady=10)
		self.email=tk.Entry(self.root)
		self.email.grid(row=3,column=1,padx=20,pady=10)
		self.contact=tk.Entry(self.root)
		self.contact.grid(row=4,column=1,padx=20,pady=10)
		self.address=tk.Text(self.root,height=4,width=15)
		self.address.grid(row=5,column=1,padx=20,pady=10)
		
		self.g=tk.StringVar()
		self.g.set('Male')
		self.r3=tk.Radiobutton(text='Male',variable=self.g,value='Male')
		self.r3.grid(row=6,column=1,padx=20,pady=10)
		self.r4=tk.Radiobutton(text='Female',variable=self.g,value='Female')
		self.r4.grid(row=6,column=2,padx=20,pady=10)
		
		self.edit=tk.Button(self.root,text='Edit',width=9,command=self.btn_edit_clicked)
		self.edit.grid(row=8,column=0,padx=20,pady=10)
		self.save=tk.Button(self.root,text='Save',width=9,command=self.btn_save_clicked)
		self.save.grid(row=8,column=1,padx=20,pady=10)
		self.cancel=tk.Button(self.root,text='Cancel',width=9,command=self.btn_cancel_clicked)
		self.cancel.grid(row=8,column=2,padx=20,pady=10)
		self.usr=UMSservices.searchbyid(self.uid)
		self.showRecord(self.usr)
		self.root.mainloop()
		
	def showRecord(self,user):
		self.editsave='view'
		self.enableAll()
		self.userid.insert(0,str(user.getUserid()))
		self.username.insert(0,str(user.getUsername()))
		self.name.insert(0,str(user.getName()))
		self.email.insert(0,str(user.getEmail()))
		self.contact.insert(0,str(user.getContact()))
		self.address.insert(1.0,str(user.getAddress()))
		if user.getGender()==0:
			self.g.set('Female')
		self.disableAll()
		self.save.config(state='disable')
	
	def enableAll(self):
		self.userid.config(state='normal')
		self.username.config(state='normal')
		self.r3.config(state='normal')
		self.r4.config(state='normal')
		self.name.config(state='normal')
		self.email.config(state='normal')
		self.contact.config(state='normal')
		self.address.config(state='normal')
		
		
	def disableAll(self):
		self.userid.config(state='disable')
		self.username.config(state='disable')
		self.r3.config(state='disable')
		self.r4.config(state='disable')
		self.name.config(state='disable')
		self.email.config(state='disable')
		self.contact.config(state='disable')
		self.address.config(state='disable')	
			
	def btn_cancel_clicked(self):
		if self.editsave=='view':
			self.root.destroy()
			m=Mainframe(self.uid,self.un)
		else:
			self.editsave='view'
			self.delete()
			self.showRecord(self.usr)
			self.edit.config(state='normal')
			
	
	def btn_edit_clicked(self):
		self.edit.config(state='disable')
		self.save.config(state='normal')
		self.enableAll()
		self.userid.config(state='disable')
		self.username.config(state='disable')
		self.editsave='edit'
	
	def btn_save_clicked(self):
		usr=user()
		usr.setName(self.name.get())
		usr.setEmail(self.email.get())
		usr.setContact(self.contact.get())
		usr.setAddress(self.address.get(1.0,'end'))
		usr.setUserid(int(self.uid))
		if self.g.get()=='Male':
			usr.setGender(1)
		else:
			usr.setGender(0)
		if UMSservices.updateprofile(usr):
			messagebox.showinfo('Success','Record updated')
		self.edit.config(state='normal')
		self.usr=UMSservices.searchbyid(self.uid)
		self.delete()
		self.showRecord(self.usr)
	def delete(self):
		self.userid.config(state='normal')
		self.username.config(state='normal')
		self.userid.delete(0,'end')
		self.username.delete(0,'end')
		self.name.delete(0,'end')
		self.email.delete(0,'end')
		self.contact.delete(0,'end')
		self.address.delete(1.0,'end')
		
	

		
	
		
