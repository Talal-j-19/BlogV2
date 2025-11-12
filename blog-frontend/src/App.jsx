import { Box, Container, VStack, Heading, Text, useToast } from "@chakra-ui/react";
import { useState } from "react";
import BlogForm from "./components/BlogForm";
import BlogResult from "./components/BlogResult";

export default function App() {
  const [blogContent, setBlogContent] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const toast = useToast();

  const generateBlog = async (data) => {
    setIsGenerating(true);
    try {
      const response = await fetch("/api/v1/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...data,
          return_markdown: true,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate blog");
      }

      const content = await response.text();
      setBlogContent(content);
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to generate blog",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Box minH="100vh" bgGradient="linear(to-br, brand.50, brand.100)">
      <Container maxW="container.lg" py={10}>
        <VStack spacing={8} align="stretch">
          <Box textAlign="center" py={10}>
            <Heading 
              as="h1" 
              size="2xl" 
              bgGradient="linear(to-r, brand.500, brand.700)"
              bgClip="text"
              mb={4}
            >
              AI Blog Generator
            </Heading>
            <Text fontSize="xl" color="gray.600">
              Create stunning blog posts with the power of AI
            </Text>
          </Box>

          <BlogForm onSubmit={generateBlog} isGenerating={isGenerating} />
          
          {blogContent && (
            <BlogResult content={blogContent} />
          )}
        </VStack>
      </Container>
    </Box>
  );
}