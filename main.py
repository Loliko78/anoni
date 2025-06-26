import wx
import wx.html2

URL = "https://anoni-1.onrender.com/"

class MyBrowser(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Harvest", size=(800, 800))
        self.browser = wx.html2.WebView.New(self)
        self.browser.LoadURL(URL)

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyBrowser()
    frame.Show()
    app.MainLoop()