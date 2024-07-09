import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:path_provider/path_provider.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:sprintf/sprintf.dart';
import 'package:google_generative_ai/google_generative_ai.dart';

import 'prompt.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Speech to Text',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(title: 'Flutter Speech to Text'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final stt.SpeechToText _speechToText = stt.SpeechToText();
  bool _isListening = false;
  String _recognizedWords = '';
  String _generatedCode = '';
  final _formKey = GlobalKey<FormState>();
  Timer? _generateCodeTimer;
  bool _canGenerateCode = true;

  @override
  void initState() {
    super.initState();
    _initSpeech();
  }
  @override
  void dispose() {
    _generateCodeTimer?.cancel();
    super.dispose();
  }

  Future<void> _initSpeech() async {
    bool available = await _speechToText.initialize(
      onStatus: (status) {
        print('Speech status: $status');
        if (status == "notListening") {
          setState(() {
            _isListening = false;
          });
        }
      },
      onError: (error) {
        print('Speech error: $error');
      },
    );
    if (available) {
      print('Speech recognition available');
    } else {
      print('Speech recognition not available');
    }
  }

  Future<void> _startListening() async {
    print("start listening called");
    try {
      stt.SpeechListenOptions opt = stt.SpeechListenOptions(listenMode : stt.ListenMode.dictation, autoPunctuation  : false, partialResults : true);
      await _speechToText.cancel();
      await _speechToText.listen(
        onResult: (result) {
          setState(() {
            _recognizedWords = result.recognizedWords.toLowerCase().replaceAll(RegExp(r'[.,!?;:]'), '');
            //print('Recognized words: $result');          
            _processTranscript(_recognizedWords);
          });
        },
        onSoundLevelChange: (level) {
          print('Sound level: $level');
        },
        listenOptions: opt
      );
      setState(() {
        _isListening = true;
      });
    } catch (e) {
      print('Error starting listening: $e');
    }
  }

  Future<void> _stopListening() async {
    await _speechToText.cancel();
    setState(() {
      _isListening = false;
    });
    print("stop done");
  }
  Future<void> _resetTranscript() async {
    setState(() {
      _recognizedWords = '';
    });
    await _stopListening();
    print("started again");
    await _startListening();
    
  }


  Future<void> _processTranscript(String transcript) async {
    print('Processing transcript: $transcript');
    // Replace this with your Gemini API call logic
    // You'll need to implement the API call and handle the response
    // For simplicity, we'll just print the transcript here
    if(transcript.contains(RegExp(r'clear')) == true){
      _resetTranscript();
      setState(() {
        print("cleared");
      });
      
      return;
    }
    _generateCode(transcript);
  }

  Future<void> _generateCode(String transcript) async {
    // Replace this with your Gemini API call logic
    // You'll need to implement the API call and handle the response
    // For simplicity, we'll just print the transcript here
   // print("called generate");
    if (!_canGenerateCode || transcript.contains(RegExp(r'send')) != true) {
      //print("Can't generate code");
      return; // Don't generate code if the flag is false
    }
    setState(() {
      _canGenerateCode = false;
    });
    _generateCodeTimer = Timer(const Duration(seconds: 5), () {
      setState(() {
        _canGenerateCode = true; // Allow code generation again
      });
    });
    print('Generating code...' + transcript);
    try { 
    String classify = sprintf(classify_prompt, [transcript]);
    const String API_KEY = String.fromEnvironment('API_KEY');
    final model = GenerativeModel(model: 'gemini-1.5-flash', apiKey: API_KEY);
    final content = [Content.text(classify)];
    final response = await model.generateContent(content);
    if (response.text != null && response.text?.contains(RegExp(r'Not related to code'))  == true){
      print("Not related");
      setState
      (() {
        _recognizedWords = "";
      }
      );
      return;
    }
    else if (response.text != null && response.text?.contains(RegExp(r'Unfinished Thought')) == true){
      print("Unfinished");
      return;
      
    }
    else if (response.text != null && response.text?.contains(RegExp(r'Finished and Code related'))  == true){
      String generate = sprintf(code_prompt, [_generatedCode, transcript]);
      final content = [Content.text(generate)];
      final response = await model.generateContent(content);
      if (response.text != null) {
        _resetTranscript();
        setState(() {
          _generatedCode = (response.text) as String;
        });
      print(response.text);
      }}
    else {
      print(response.text);
    }
    }
    catch (e){
      print("Generation failed");
      print(e);
    }
  
     
    /*try {
      final response = await http.post(
        Uri.parse('https://your-gemini-api-endpoint.com'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'prompt': 'Generate code based on this transcript: $transcript',
        }),
      );
      if (response.statusCode == 200) {
        setState(() {
          _generatedCode = jsonDecode(response.body)['code'];
        });
      } else {
        print('Error generating code: ${response.statusCode}');
      }
    } catch (e) {
      print('Error generating code: $e');
    }*/
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Text(
                  'Recognized words:',
                  style: TextStyle(fontSize: 18),
                ),
                SizedBox(height: 16),
                Text(
                  _recognizedWords,
                  style: TextStyle(fontSize: 16),
                ),
                SizedBox(height: 32),
                ElevatedButton(
                  onPressed: _isListening ? _stopListening : _startListening,
                  child: Text(_isListening ? 'Stop Listening' : 'Start Listening'),
                ),
                SizedBox(height: 32),
                Text(
                  'Generated Code:',
                  style: TextStyle(fontSize: 18),
                ),
                SizedBox(height: 16),
                Text(
                  _generatedCode,
                  style: TextStyle(fontSize: 16),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
