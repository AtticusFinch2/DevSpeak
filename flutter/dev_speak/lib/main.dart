import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:path_provider/path_provider.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
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

  @override
  void initState() {
    super.initState();
    _initSpeech();
  }

  Future<void> _initSpeech() async {
    bool available = await _speechToText.initialize(
      onStatus: (status) {
        print('Speech status: $status');
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
    try {
      await _speechToText.listen(
        onResult: (result) {
          setState(() {
            _recognizedWords = result.recognizedWords;
            print('Recognized words: $result');
            _processTranscript(_recognizedWords);
          });
        },
        onSoundLevelChange: (level) {
          print('Sound level: $level');
        },
      );
      setState(() {
        _isListening = true;
      });
    } catch (e) {
      print('Error starting listening: $e');
    }
  }

  Future<void> _stopListening() async {
    await _speechToText.stop();
    setState(() {
      _isListening = false;
    });
  }

  Future<void> _processTranscript(String transcript) async {
    // Replace this with your Gemini API call logic
    // You'll need to implement the API call and handle the response
    // For simplicity, we'll just print the transcript here
    print('Transcript: $transcript');
    _generateCode(transcript);
  }

  Future<void> _generateCode(String transcript) async {
    // Replace this with your Gemini API call logic
    // You'll need to implement the API call and handle the response
    // For simplicity, we'll just print the transcript here
    print('Generating code...');
    try {
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
    }
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
