from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from os import listdir
from models import MatrixItem, IntegrityCheck, MatrixAnswer
import datetime
from pytz import timezone
from django.contrib.auth.models import User
from numpy import around
from datetime import datetime
from time import strptime

@login_required
def submitIntegrityCheck(request):
    relatedMatrixItem = get_object_or_404(MatrixItem, fileID = request.GET['fileID'])

    print request.GET['correct']

    #check if it already exists
    try:
        previousIntegrityCheck = IntegrityCheck.objects.get(matrixItem=relatedMatrixItem, rater = request.user)
        previousIntegrityCheck.requirements = request.GET['requirements'] == 'yes'
        previousIntegrityCheck.correct = request.GET['correct'] == 'yes'
        previousIntegrityCheck.nominated = request.GET['nominated'] == 'yes'
        previousIntegrityCheck.comments = request.GET['comments']
        previousIntegrityCheck.save()
        
        
    except IntegrityCheck.DoesNotExist:
        newIntegrityCheck = IntegrityCheck(matrixItem = relatedMatrixItem,
                                            rater = request.user,
                                            requirements = request.GET['requirements'] == 'yes',
                                            correct = request.GET['correct'] == 'yes',
                                            nominated = request.GET['nominated'] == 'yes',
                                            comments = request.GET['comments'])

        newIntegrityCheck.save()

    return HttpResponseRedirect('/viewSubmissions')

@login_required
def viewAccepted(request):
	pass

@login_required
def checkStatus(request):
	allCheckerNames = ['engel', 'chabris', 'eric', 'jackie']
	checkerCounts = [0,0,0,0]
	
	allCheckers = [User.objects.get(username = curChecker) for curChecker in allCheckerNames]
	allMatrixItems = MatrixItem.objects.all()
	updatedMatrixItems = []
	
	for curItem in allMatrixItems:
		curItem.checked = []
		curItem.accepted = []
		for curID, curChecker in enumerate(allCheckers):
			checked, accepted = curItem.checkedAndAcceptedByUser(curChecker)
			curItem.checked.append( checked )
			curItem.accepted.append( accepted )
			if checked:
				checkerCounts[curID] += 1

#		if not accepted and not curItem.status == 'Rejected':
#			curItem.status = 'Rejected'
#			curItem.save()
		updatedMatrixItems.append(curItem)
		
		status = 'Pending'
		numAccepts = 0
		for curChecked, curAccepted in zip(curItem.checked, curItem.accepted):
			if curChecked and not curAccepted:
				status = 'Rejected'
				break
			if curChecked and curAccepted:
				numAccepts += 1
		
			if numAccepts >= 3:
				status = 'Accepted'
		
		if not curItem.status == status:
			curItem.status = status
			curItem.save()
	
	allMatrixItems = updatedMatrixItems
	context = {'allMatrixItems':allMatrixItems, 'checkerNames':allCheckerNames, 'checkerCounts':checkerCounts}
	return render(request, 'checkStatus.html', context)

@login_required
def viewSubmissions(request):
    allMatrixItems = MatrixItem.objects.all()
    updatedMatrixItems = []
    for curItem in allMatrixItems:
        curItem.checked = curItem.checkedByUser(request.user)
        updatedMatrixItems.append(curItem)
    
    allMatrixItems = updatedMatrixItems
    context = {'allMatrixItems':allMatrixItems}
    return render(request, 'viewSubmissions.html', context)

def loginUser(request):
    context = {'userName': request.COOKIES.get('username')}
    if context['userName'] == None:
        context['userName'] = ''
    return render(request, 'loginUser.html', context)

def completed(request):
    return render(request, 'completed.html')

def nextPuzzle(request):
    if request.COOKIES.get('username') == None:
        return HttpResponseRedirect('/login')
    
    if int(request.COOKIES.get('completedCount')) >= 3:
        response = HttpResponseRedirect('/completed')
        response.set_cookie("username", '')
        return response
        
    if not request.COOKIES.get('curMatrixItem'):
        pickedMatrixItem = MatrixItem.objects.order_by('?')[0]
    else:
        pickedMatrixItem = MatrixItem.objects.get(fileID = request.COOKIES.get('curMatrixItem'))

    context = {'userName': request.COOKIES.get('username'), 'matrixItem':pickedMatrixItem, 'completedCount':request.COOKIES.get('completedCount')}
    response = render(request, 'nextPuzzle.html', context)
    response.set_cookie("curMatrixItem", pickedMatrixItem.fileID)
    
    if not request.COOKIES.get('startTime'):
        startTime = datetime.now()
        response.set_cookie("startTime", startTime)
    else:
        startTime = request.COOKIES.get('curMatrixItem')

    return response

def setCookie(request):
    response = HttpResponseRedirect('/nextPuzzle')
    response.set_cookie("username", request.GET['userName'])
    response.set_cookie("curMatrixItem", '')
    response.set_cookie("startTime", '')
    response.set_cookie("completedCount", "0")
    return response

def submitAnswer(request):
    answer = MatrixAnswer(matrixItem = MatrixItem.objects.get(fileID = request.COOKIES.get('curMatrixItem')),
                           userName = request.COOKIES.get('username'),
                           answer = int(request.GET['answer']),
                           startTime = datetime.strptime(request.COOKIES.get('startTime'), '%Y-%m-%d %H:%M:%S.%f'),
                           endTime = datetime.now(),
                           timeTaken = (datetime.now() - datetime.strptime(request.COOKIES.get('startTime'), '%Y-%m-%d %H:%M:%S.%f')).total_seconds())
                           #endTime = 
                           #timeTaken = 
    answer.save()
    response = HttpResponseRedirect('/nextPuzzle')
    response.set_cookie("curMatrixItem", '')
    response.set_cookie("startTime", '')
    response.set_cookie("completedCount", str(int(request.COOKIES.get('completedCount')) + 1))
    return response
    
@login_required
def frontPage(request):
    allMatrixItems = MatrixItem.objects.all()
    allIntegrityChecks = IntegrityCheck.objects.all()
    yourIntegrityChecks = IntegrityCheck.objects.filter( rater = request.user)
    
    context = {'yourIntegrityChecks': len(yourIntegrityChecks), 'yourPercentChecks': float(len(yourIntegrityChecks))/float(len(allMatrixItems))*100.0 , 'numMatrixItems': len(allMatrixItems), 'numIntegrityChecks':len(allIntegrityChecks), 'portionIntegrityChecks':around(100*(float(len(allIntegrityChecks)) / float(len(allMatrixItems)) / 4.0),4)}
    return render(request, 'frontpage.html', context)

@login_required
def integrityCheck(request, submission_id):
    curMatrixItems = get_object_or_404(MatrixItem, fileID=submission_id)
    context = {'matrixItem':curMatrixItems}
    return render(request, 'integrityCheck.html', context)

@login_required
def updateDB(request):
    MatrixItemBaseDir = 'CleanedItems/'
    allFiles = listdir(MatrixItemBaseDir)
    allItems = [curFile for curFile in allFiles if '.' in curFile]
    
    rejectedItems = []
    acceptedItems = []
    
    for curItem in allItems:
        [fileID, fileExtension] = curItem.split('.')

        if fileExtension not in ['jpg', 'png']:
            rejectedItems.append(([curItem, 'Unsupported Image Format: ' + curItem.split('.')[1].lower()]))
            continue

        if fileID not in allFiles:
            rejectedItems.append(([curItem, 'No data file present']))
            continue
        
        if not MatrixItem.objects.filter(fileID=fileID).count():
            fp = open(MatrixItemBaseDir + fileID, 'r')
            allData = fp.readlines()
            
            name = allData[1][6:].strip()
            email = allData[2][7:].strip()
            updates = allData[3][9:].strip()
            difficulty = allData[4][12:].strip()
            correctAnswer = allData[5][8:].strip()
            timestamp = curItem.split('.')[0]
            filesize = allData[-2][10:].strip()
            filetype = allData[-1][10:].strip()
            explanation = allData[6:-4]
            explanation = '\n'.join(explanation)[24:]

            utc=timezone('US/Eastern')

            newItem = MatrixItem(fileID = fileID,
                                    filename = curItem,
                                    name = name,
                                    email = email,
                                    updates = updates,
                                    reported_Difficulty = difficulty,
                                    reported_CorrectAnswer = correctAnswer,
                                    timestampSubmitted = utc.localize(datetime.datetime.fromtimestamp(int(timestamp))),
                                    filesize = filesize,
                                    filetype = filetype,
                                    explanation = explanation)
            
            newItem.save()
            acceptedItems.append(curItem)
        else:
            rejectedItems.append(([curItem, 'Already in DB']))
            continue
            
        
    
            
    
    resText = '<h3>New Accepted Items </h3>'
    for curAcceptedItems in acceptedItems:
        resText += curAcceptedItems + ' <br>'

    resText += '<h3>Rejected Items </h3>'
    for curRejectedItem in rejectedItems:
        resText += curRejectedItem[0] + ' - ' + curRejectedItem[1] + ' <br>'
    return HttpResponse(resText)
