import 'package:flutter/material.dart';
import 'http:^1.2.0'; // تمثيل استيراد المكتبة
import 'dart:convert';

void main() {
  runApp(const SmartAgriApp());
}

class SmartAgriApp extends StatelessWidget {
  const SmartAgriApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Agriculture & Payments',
      theme: ThemeData(
        primarySwatch: Colors.green,
        useMaterial3: true,
      ),
      home: const AgriHomePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class AgriHomePage extends StatefulWidget {
  const AgriHomePage({super.key});

  @override
  State<AgriHomePage> createState() => _AgriHomePageState();
}

class _AgriHomePageState extends State<AgriHomePage> {
  // استبدل هذا الرابط برابط الـ Backend الدائم الخاص بك (مثلاً من Render أو Railway)
  final String backendUrl = "https://your-backend-url.onrender.com/api/v1/payments/";
  
  List payments = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchPayments();
  }

  // جلب البيانات من الـ Backend
  Future<void> fetchPayments() async {
    try {
      final response = await http.get(Uri.parse(backendUrl));
      if (response.statusCode == 200) {
        setState(() {
          payments = json.decode(response.body);
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      // التعامل مع الأخطاء إن وجدت
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('منصة الزراعة الذكية والمدفوعات'),
        backgroundColor: Colors.green[700],
        foregroundColor: Colors.white,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'سجل المعاملات السحابية:',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  Expanded(
                    child: payments.isEmpty
                        ? const Center(child: Text('لا توجد معاملات مسجلة حتى الآن.'))
                        : ListView.builder(
                            itemCount: payments.length,
                            itemBuilder: (context, index) {
                              final item = payments[index];
                              return Card(
                                elevation: 3,
                                margin: const EdgeInsets.symmetric(vertical: 6),
                                child: ListTile(
                                  leading: const Icon(Icons.payment, color: Colors.green),
                                  title: Text('العميل: ${item['customer_name']}'),
                                  subtitle: Text('المبلغ: ${item['amount']} ${item['currency']}'),
                                  trailing: Text(
                                    item['status'],
                                    style: const TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // هنا يمكنك إضافة شاشة أو نافذة لإرسال بيانات جديدة للـ Backend
          fetchPayments(); // تحديث القائمة عند الضغط
        },
        backgroundColor: Colors.green[700],
        child: const Icon(Icons.refresh, color: Colors.white),
      ),
    );
  }
}
