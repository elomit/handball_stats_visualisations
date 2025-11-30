# Script to convert PPT to PDF.

def ppt_to_pdf(inputFileName, outputFileName, formatType=32):
	import comtypes.client
	powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
	powerpoint.Visible = 1

	if outputFileName[-3:] != 'pdf':
		outputFileName = outputFileName + ".pdf"
	deck = powerpoint.Presentations.Open(inputFileName)
	deck.SaveAs(outputFileName, formatType)
	deck.Close()
	powerpoint.Quit()
